# pages/2_Disease_Detection.py
import streamlit as st
import os
from PIL import Image
import torch
from transformers import ViTForImageClassification, ViTImageProcessor
import glob
import json

class DiseaseDetectionPage:
    def __init__(self):
        self.setup_page()
        
        # Initialize session state
        if 'model_loaded' not in st.session_state:
            st.session_state.model_loaded = False
        if 'model' not in st.session_state:
            st.session_state.model = None
        if 'processor' not in st.session_state:
            st.session_state.processor = None
        if 'results' not in st.session_state:
            st.session_state.results = None
        if 'show_results' not in st.session_state:
            st.session_state.show_results = False
    
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
            model_path = "disease_detection/plant_disease_vit_model"
            
            if not os.path.exists(model_path):
                st.error(f"❌ Model folder not found at: {model_path}")
                return False
            
            # Load config to check classes
            config_path = os.path.join(model_path, "model_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                st.session_state.model_config = config_data
            else:
                st.session_state.model_config = {}
            
            # Load processor and model
            st.session_state.processor = ViTImageProcessor.from_pretrained(model_path)
            st.session_state.model = ViTForImageClassification.from_pretrained(
                model_path,
                local_files_only=True,
                ignore_mismatched_sizes=True
            )
            
            st.session_state.model.eval()
            st.session_state.model_loaded = True
            
            # Analyze classes from config
            self.analyze_classes()
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error loading model: {str(e)}")
            return False
    
    def analyze_classes(self):
        """Analyze and count different types of classes"""
        if not hasattr(st.session_state, 'model_config'):
            return
            
        id2label = st.session_state.model_config.get('id2label', {})
        
        # Initialize collections
        plant_types_set = set()
        healthy_classes_list = []
        disease_classes_list = []
        all_classes_list = []
        
        for label in id2label.values():
            all_classes_list.append(label)
            
            if "___" in label:
                plant_part, disease_part = label.split("___", 1)
                plant_name = plant_part.replace("_", " ").title()
                plant_types_set.add(plant_name)
                
                if "healthy" in disease_part.lower():
                    healthy_classes_list.append(label)
                else:
                    disease_classes_list.append(label)
        
        # Store in session state
        st.session_state.plant_types = sorted(list(plant_types_set))
        st.session_state.healthy_classes = sorted(healthy_classes_list)
        st.session_state.disease_classes = sorted(disease_classes_list)
        st.session_state.all_classes = sorted(all_classes_list)
    
    def load_test_images(self):
        """Load test images from folder"""
        test_images_path = "disease_detection/test_images"
        if not os.path.exists(test_images_path):
            return []
        
        # Find image files
        image_files = glob.glob(os.path.join(test_images_path, "*.*"))
        image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        # Limit to first 4 images
        return image_files[:4]
    
    def predict_disease(self, image_path):
        """Predict disease from image using ViT model"""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert("RGB")
            inputs = st.session_state.processor(images=image, return_tensors="pt")
            
            # Run inference
            with torch.no_grad():
                outputs = st.session_state.model(**inputs)
                logits = outputs.logits
            
            # Get predictions
            probs = torch.nn.functional.softmax(logits, dim=-1)
            confidence, class_idx = torch.max(probs, dim=-1)
            
            # Get label from model config
            class_id = str(class_idx.item())
            if hasattr(st.session_state.model.config, 'id2label') and class_id in st.session_state.model.config.id2label:
                predicted_label = st.session_state.model.config.id2label[class_id]
            elif hasattr(st.session_state, 'model_config') and class_id in st.session_state.model_config.get('id2label', {}):
                predicted_label = st.session_state.model_config['id2label'][class_id]
            else:
                predicted_label = f"Class_{class_id}"
                
            confidence_score = confidence.item()
            
            return predicted_label, confidence_score
            
        except Exception as e:
            return f"Error: {str(e)}", 0.0
    
    def parse_prediction_label(self, predicted_label):
        """Parse the prediction label into plant name, status, and disease type"""
        try:
            if "___" in predicted_label:
                # Format: "Plant___Disease" or "Plant___healthy"
                plant_part, disease_part = predicted_label.split("___", 1)
                
                # Plant name (before underscore)
                plant_name = plant_part.replace("_", " ").title()
                
                # Check if healthy
                if "healthy" in disease_part.lower():
                    status = "Healthy"
                    disease_type = "None"
                else:
                    status = "Diseased"
                    # Disease type (after underscore)
                    disease_type = disease_part.replace("_", " ").title()
                
                return plant_name, status, disease_type
            else:
                # Handle unknown format
                if "Class_" in predicted_label:
                    return "Unknown Plant", "Unknown", "Unknown Disease"
                else:
                    # Try to parse anyway
                    return "Unknown", "Unknown", predicted_label.replace("_", " ").title()
                
        except:
            return "Unknown", "Unknown", "Unknown"
    
    def get_border_color(self, status, confidence):
        """Get border color based on status and confidence"""
        if status == "Healthy":
            return "#28a745"  # Green for healthy
        elif status == "Diseased":
            if confidence > 0.7:
                return "#dc3545"   # Red for high confidence disease
            elif confidence > 0.5:
                return "#ffc107"   # Yellow for medium confidence disease
            else:
                return "#6c757d"   # Gray for low confidence
        else:
            return "#6c757d"   # Gray for unknown
    
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
    
    def render_model_configuration(self):
        """Render model configuration section"""
        st.subheader("⚙️ Model Configuration")
        
        if st.session_state.model_loaded and st.session_state.model:
            # Get model info
            model_type = "Vision Transformer (ViT)"
            image_size = st.session_state.model.config.image_size
            
            # Display model info in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Model Type", model_type)
            with col2:
                st.metric("Image Size", f"{image_size}x{image_size}")
            
            # Show classes summary in expander
            with st.expander("📋 View Model Classes Details"):
                # Get lists from session state
                plant_types = getattr(st.session_state, 'plant_types', [])
                healthy_classes = getattr(st.session_state, 'healthy_classes', [])
                disease_classes = getattr(st.session_state, 'disease_classes', [])
                all_classes = getattr(st.session_state, 'all_classes', [])
                
                st.write(f"**Plant Types ({len(plant_types)}):**")
                for plant in plant_types:
                    st.write(f"  • {plant}")
                
                st.write(f"\n**Healthy Classes ({len(healthy_classes)}):**")
                for healthy in healthy_classes[:5]:  # Show first 5
                    st.write(f"  • {healthy}")
                if len(healthy_classes) > 5:
                    st.write(f"  • ... and {len(healthy_classes) - 5} more")
                
                st.write(f"\n**Disease Classes ({len(disease_classes)}):**")
                for disease in disease_classes[:5]:  # Show first 5
                    st.write(f"  • {disease}")
                if len(disease_classes) > 5:
                    st.write(f"  • ... and {len(disease_classes) - 5} more")
                
                st.write(f"\n**Total Classes ({len(all_classes)}):**")
                # Show all classes in a compact format
                classes_text = ", ".join(all_classes[:8])  # Show first 8
                if len(all_classes) > 8:
                    classes_text += f"... and {len(all_classes) - 8} more"
                st.caption(classes_text)
        else:
            st.warning("⚠️ Model not loaded")
            if st.button("🔄 Load Model", type="primary"):
                with st.spinner("Loading model..."):
                    if self.load_model():
                        st.rerun()
    
    def render_input_images(self):
        """Render input images section - only show when not showing results"""
        if not st.session_state.show_results:
            st.subheader("📁 Input Samples")
            
            # Load images
            test_images = self.load_test_images()
            
            if not test_images:
                st.warning("No test images found in 'disease_detection/test_images/' folder")
                return
            
            # Display images in columns
            cols = st.columns(4)
            for i, image_path in enumerate(test_images):
                with cols[i]:
                    try:
                        image = Image.open(image_path)
                        st.image(image, use_container_width=True, caption=f"Sample {i+1}")
                    except Exception:
                        st.error("Error loading image")
            
            # Store images in session state for processing
            st.session_state.test_images = test_images
            
            # Run analysis button
            if st.session_state.model_loaded:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🎯 Run Disease Analysis", type="primary", use_container_width=True):
                        with st.spinner("Analyzing plant images..."):
                            results = []
                            for image_path in st.session_state.test_images:
                                # Predict disease
                                predicted_label, confidence = self.predict_disease(image_path)
                                plant_name, status, disease_type = self.parse_prediction_label(predicted_label)
                                
                                results.append({
                                    'image_path': image_path,
                                    'plant_name': plant_name,
                                    'status': status,
                                    'disease_type': disease_type,
                                    'confidence': confidence,
                                    'border_color': self.get_border_color(status, confidence)
                                })
                            
                            # Store results and show results section
                            st.session_state.results = results
                            st.session_state.show_results = True
                            st.rerun()
    
    def render_results(self):
        """Render detection results"""
        if not st.session_state.show_results or st.session_state.results is None:
            return
        
        st.subheader("🔍 Analysis Results")
        
        # Back button to go to input images
        if st.button("← Back to Input Images"):
            st.session_state.show_results = False
            st.session_state.results = None
            st.rerun()
        
        # Create columns for results
        cols = st.columns(4)
        
        for i, result in enumerate(st.session_state.results):
            with cols[i]:
                # Remove the empty border div - just show image directly
                try:
                    image = Image.open(result['image_path'])
                    # Create a caption with border color indicator
                    border_color = result['border_color']
                    status_indicator = "🟢" if result['status'] == "Healthy" else "🔴" if result['confidence'] > 0.7 else "🟡"
                    st.image(image, use_container_width=True, caption=f"{status_indicator} Sample {i+1}")
                    
                    # Display prediction info in a clean card with border
                    st.markdown(f"""
                    <div style="border-left: 4px solid {border_color}; padding: 10px 15px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 10px;">
                    """, unsafe_allow_html=True)
                    
                    # Plant name
                    if result['plant_name'] != "Unknown":
                        st.markdown(f"**🌿 Plant:** {result['plant_name']}")
                    else:
                        st.markdown(f"**🌿 Plant:** Unknown")
                    
                    # Status with icon
                    if result['status'] == "Healthy":
                        status_icon = "✅"
                        status_color = "green"
                        status_text = "Healthy"
                    elif result['status'] == "Diseased":
                        status_icon = "🦠"
                        status_color = "red"
                        status_text = "Diseased"
                    else:
                        status_icon = "❓"
                        status_color = "gray"
                        status_text = "Unknown"
                    
                    st.markdown(f"**{status_icon} Status:** <span style='color:{status_color};'>{status_text}</span>", unsafe_allow_html=True)
                    
                    # Disease type (only show if diseased and not "None")
                    if result['status'] == "Diseased" and result['disease_type'] != "None" and result['disease_type'] != "Unknown":
                        st.markdown(f"**📋 Disease:** {result['disease_type']}")
                    
                    # Confidence score
                    confidence_score = result['confidence'] * 100
                    if confidence_score > 0:
                        # Color code confidence
                        if confidence_score > 70:
                            conf_color = "#28a745"
                        elif confidence_score > 50:
                            conf_color = "#ffc107"
                        else:
                            conf_color = "#dc3545"
                        
                        st.markdown(f"**📈 Confidence:** <span style='color:{conf_color}; font-weight: bold;'>{confidence_score:.1f}%</span>", unsafe_allow_html=True)
                        
                        # Progress bar
                        st.progress(result['confidence'])
                    else:
                        st.markdown("**📈 Confidence:** N/A")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Error displaying result: {e}")
    
    def run(self):
        """Run the disease detection page"""
        self.render_sidebar()
        self.render_header()
        
        # Auto-load model if not loaded
        if not st.session_state.model_loaded:
            with st.spinner("Loading disease detection model..."):
                if self.load_model():
                    st.success("✅ Model loaded successfully!")
        
        # Show model configuration
        self.render_model_configuration()
        st.markdown("---")
        
        # Show either input images or results
        if not st.session_state.show_results:
            self.render_input_images()
        else:
            self.render_results()

# Initialize and run disease detection page
if __name__ == "__main__":
    disease_page = DiseaseDetectionPage()
    disease_page.run()