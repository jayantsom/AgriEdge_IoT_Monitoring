# pages/2_Disease_Detection.py
import streamlit as st
import os
from PIL import Image
import torch
from transformers import ViTForImageClassification, ViTImageProcessor
import glob

class DiseaseDetectionPage:
    def __init__(self):
        self.setup_page()
        self.model_loaded = False
        self.model = None
        self.processor = None
    
    def setup_page(self):
        """Setup page configuration"""
        st.set_page_config(
            page_title="Disease Detection - AgriEdge", 
            page_icon="🦠",
            layout="wide"
        )
    
    def load_model(self):
        """Load the ViT model and processor"""
        try:
            model_path = "plant_disease_vit_model"
            
            if not os.path.exists(model_path):
                st.error(f"❌ Model folder not found at: {model_path}")
                return False
            
            # Check for model files
            model_files = os.listdir(model_path)
            st.info(f"📁 Model files found: {model_files}")
            
            # Load processor and model
            self.processor = ViTImageProcessor.from_pretrained(model_path)
            
            # Try loading with different model file names
            if "model.safetensors" in model_files:
                self.model = ViTForImageClassification.from_pretrained(model_path)
            elif "pytorch_model.bin" in model_files:
                self.model = ViTForImageClassification.from_pretrained(model_path)
            else:
                st.error("❌ No valid model file found (model.safetensors or pytorch_model.bin)")
                return False
            
            self.model.eval()  # Set to evaluation mode
            self.model_loaded = True
            st.success("✅ Model loaded successfully!")
            return True
            
        except Exception as e:
            st.error(f"❌ Error loading model: {str(e)}")
            return False
    
    def predict_disease(self, image_path):
        """Predict disease from image using ViT model"""
        if not self.model_loaded:
            return "Model not loaded", 0.0
        
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt")
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
            
            # Get predictions
            probs = torch.nn.functional.softmax(logits, dim=-1)
            confidence, class_idx = torch.max(probs, dim=-1)
            
            # Get label from model config
            predicted_label = self.model.config.id2label[str(class_idx.item())]
            confidence_score = confidence.item()
            
            return predicted_label, confidence_score
            
        except Exception as e:
            return f"Error: {str(e)}", 0.0
    
    def parse_prediction(self, predicted_label):
        """Parse the prediction label into plant and disease info"""
        try:
            # Split the label into plant and disease parts
            if "___" in predicted_label:
                plant_part, disease_part = predicted_label.split("___", 1)
                
                # Clean up plant name
                plant = plant_part.replace("_", " ").title()
                
                # Check if healthy
                if "healthy" in disease_part.lower():
                    disease = "Healthy"
                else:
                    disease = disease_part.replace("_", " ").title()
                
                return plant, disease
            else:
                return "Unknown", predicted_label.replace("_", " ").title()
                
        except:
            return "Unknown", predicted_label
    
    def get_border_color(self, disease_status, confidence):
        """Get border color based on disease status and confidence"""
        if "healthy" in disease_status.lower():
            return "#28a745"  # Green for healthy
        elif confidence > 0.7:
            return "#dc3545"   # Red for high confidence disease
        elif confidence > 0.5:
            return "#ffc107"   # Yellow for medium confidence disease
        else:
            return "#6c757d"   # Gray for low confidence
    
    def render_sidebar(self):
        """Render sidebar with page navigation only"""
        with st.sidebar:
            st.title("🌱 AgriEdge")
            st.markdown("---")
            
            # Page Navigation with descriptions
            st.subheader("📄 Navigation")
            
            # Dashboard Page
            if st.button("📊 **Live Dashboard**", width='stretch'):
                st.switch_page("streamlit_app.py")
            
            st.caption("Real-time sensor monitoring & analytics")
            st.markdown("---")
            
            # Disease Detection Page
            if st.button("🦠 **Disease Detection**", width='stretch'):
                st.rerun()  # Already on disease detection page
            
            st.caption("AI-powered plant disease detection & analysis")
            st.markdown("---")
            
            st.caption("Smart Farming AI System")
    
    def render_header(self):
        """Render page header"""
        st.title("🦠 Disease Detection")
        st.markdown("AI-powered plant disease detection using Vision Transformer (ViT)")
        st.markdown("---")
    
    def render_model_status(self):
        """Render model loading status and controls"""
        st.subheader("🔧 Model Configuration")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if not self.model_loaded:
                st.warning("⚠️ Model not loaded")
                if st.button("🔄 Load Disease Detection Model", type="primary"):
                    with st.spinner("Loading ViT model..."):
                        if self.load_model():
                            st.rerun()
            else:
                st.success("✅ ViT Model Loaded")
                st.info(f"Model: Vision Transformer (ViT-Base)")
                st.info(f"Classes: {len(self.model.config.id2label)} plant disease categories")
        
        with col2:
            test_images_path = "disease_detection/test_images"
            if os.path.exists(test_images_path):
                image_files = glob.glob(os.path.join(test_images_path, "*.*"))
                image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                st.metric("Test Images", len(image_files))
            else:
                st.error("❌ Test images folder not found")
    
    def render_detection_results(self):
        """Render disease detection results"""
        st.subheader("🔍 Disease Detection Results")
        
        if not self.model_loaded:
            st.info("👆 Please load the model first to start disease detection")
            return
        
        # Get test images
        test_images_path = "disease_detection/test_images"
        if not os.path.exists(test_images_path):
            st.error(f"❌ Test images folder not found at: {test_images_path}")
            st.info("Please create a 'disease_detection/test_images' folder with plant images")
            return
        
        # Find image files
        image_files = glob.glob(os.path.join(test_images_path, "*.*"))
        image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not image_files:
            st.warning("📷 No images found in test_images folder")
            st.info("Supported formats: JPG, JPEG, PNG")
            return
        
        # Limit to first 4 images
        images_to_process = image_files[:4]
        
        # Process images in batches
        if st.button("🎯 Run Disease Detection", type="primary"):
            with st.spinner("Analyzing plant images..."):
                # Create columns for images
                cols = st.columns(4)
                
                results = []
                for i, image_path in enumerate(images_to_process):
                    # Predict disease
                    predicted_label, confidence = self.predict_disease(image_path)
                    plant, disease = self.parse_prediction(predicted_label)
                    
                    results.append({
                        'image_path': image_path,
                        'plant': plant,
                        'disease': disease,
                        'confidence': confidence,
                        'border_color': self.get_border_color(disease, confidence)
                    })
                
                # Display results
                for i, result in enumerate(results):
                    with cols[i]:
                        # Display image with border
                        image = Image.open(result['image_path'])
                        
                        # Create styled container
                        border_color = result['border_color']
                        st.markdown(f"""
                        <div style="border: 3px solid {border_color}; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.image(image, use_column_width=True, caption=os.path.basename(result['image_path']))
                        
                        # Display prediction info
                        st.markdown(f"**Plant:** {result['plant']}")
                        st.markdown(f"**Disease:** {result['disease']}")
                        st.markdown(f"**Confidence:** {result['confidence']*100:.1f}%")
                        
                        # Color code the confidence
                        confidence_color = "#28a745" if result['confidence'] > 0.7 else "#ffc107" if result['confidence'] > 0.5 else "#dc3545"
                        st.markdown(f"<p style='color: {confidence_color}; font-weight: bold;'>Confidence: {result['confidence']*100:.1f}%</p>", unsafe_allow_html=True)
        
        else:
            # Show preview of images without processing
            cols = st.columns(4)
            for i, image_path in enumerate(images_to_process):
                with cols[i]:
                    image = Image.open(image_path)
                    st.image(image, use_column_width=True, caption=f"Image {i+1}")
                    st.caption("Click 'Run Disease Detection' to analyze")
    
    def render_class_info(self):
        """Render information about disease classes"""
        if self.model_loaded:
            with st.expander("📋 Supported Plant Diseases (38 Classes)"):
                # Group by plant type
                plants_dict = {}
                for class_id, label in self.model.config.id2label.items():
                    if "___" in label:
                        plant, disease = label.split("___", 1)
                        if plant not in plants_dict:
                            plants_dict[plant] = []
                        plants_dict[plant].append(disease.replace("_", " ").title())
                
                for plant, diseases in plants_dict.items():
                    plant_name = plant.replace("_", " ").title()
                    st.write(f"**{plant_name}**")
                    for disease in diseases:
                        status = "✅ Healthy" if "Healthy" in disease else "🦠 Disease"
                        st.write(f"  - {disease} ({status})")
    
    def run(self):
        """Run the disease detection page"""
        self.render_sidebar()
        self.render_header()
        self.render_model_status()
        self.render_detection_results()
        self.render_class_info()

# Initialize and run disease detection page
if __name__ == "__main__":
    disease_page = DiseaseDetectionPage()
    disease_page.run()