# pages/2_Disease_Detection.py
import streamlit as st
import os
from PIL import Image
import torch
from transformers import ViTForImageClassification, ViTImageProcessor, ViTConfig
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
        if 'test_images' not in st.session_state:
            st.session_state.test_images = []
    
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
            
            # Load config file
            config_path = os.path.join(model_path, "model_config.json")
            if not os.path.exists(config_path):
                st.error(f"❌ Config file not found: {config_path}")
                return False
            
            # Load and parse config
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            
            # Create config object with correct number of labels
            config_dict['num_labels'] = len(config_dict.get('id2label', {}))
            config = ViTConfig.from_dict(config_dict)
            
            # Load processor
            st.session_state.processor = ViTImageProcessor.from_pretrained(model_path)
            
            # Create model with correct config (38 classes)
            st.session_state.model = ViTForImageClassification(config)
            
            # Try to load weights from different file formats
            weights_loaded = False
            
            # Try safetensors first
            safetensors_path = os.path.join(model_path, "model.safetensors")
            if os.path.exists(safetensors_path):
                try:
                    from safetensors.torch import load_file
                    state_dict = load_file(safetensors_path)
                    st.session_state.model.load_state_dict(state_dict, strict=False)
                    weights_loaded = True
                except Exception as e:
                    st.warning(f"Failed to load .safetensors: {e}")
            
            # Try pytorch_model.bin
            if not weights_loaded:
                bin_path = os.path.join(model_path, "pytorch_model.bin")
                if os.path.exists(bin_path):
                    try:
                        state_dict = torch.load(bin_path, map_location=torch.device('cpu'))
                        st.session_state.model.load_state_dict(state_dict, strict=False)
                        weights_loaded = True
                    except Exception as e:
                        st.warning(f"Failed to load .bin: {e}")
            
            # Try model.pth
            if not weights_loaded:
                pth_path = os.path.join(model_path, "model.pth")
                if os.path.exists(pth_path):
                    try:
                        state_dict = torch.load(pth_path, map_location=torch.device('cpu'))
                        st.session_state.model.load_state_dict(state_dict, strict=False)
                        weights_loaded = True
                    except Exception as e:
                        st.warning(f"Failed to load .pth: {e}")
            
            if not weights_loaded:
                st.error("❌ No weight file found or all failed to load")
                return False
            
            # Move model to CPU and set to eval mode
            st.session_state.model.to('cpu')
            st.session_state.model.eval()
            st.session_state.model_loaded = True
            
            # Store model config for label lookup
            st.session_state.model_config = config_dict
            
            # Analyze classes from config
            self.analyze_classes(config_dict)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error loading model: {str(e)}")
            return False
    
    def analyze_classes(self, config_dict):
        """Analyze and count different types of classes"""
        id2label = config_dict.get('id2label', {})
        
        # Initialize collections
        plant_types_set = set()
        healthy_classes_list = []
        disease_classes_list = []
        all_classes_list = []
        
        for class_id, label in sorted(id2label.items(), key=lambda x: int(x[0])):
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
        st.session_state.healthy_classes = healthy_classes_list
        st.session_state.disease_classes = disease_classes_list
        st.session_state.all_classes = all_classes_list
    
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
            
            # Move inputs to CPU
            inputs = {k: v.to('cpu') for k, v in inputs.items()}
            
            # Run inference
            with torch.no_grad():
                outputs = st.session_state.model(**inputs)
                logits = outputs.logits
            
            # Get predictions
            probs = torch.nn.functional.softmax(logits, dim=-1)
            confidence, class_idx = torch.max(probs, dim=-1)
            
            # Get class_id
            class_id = class_idx.item()
            
            # Get label from model config - try multiple sources
            predicted_label = ""
            
            # Try to get from model.config.id2label first
            if hasattr(st.session_state.model.config, 'id2label'):
                if isinstance(st.session_state.model.config.id2label, dict):
                    if str(class_id) in st.session_state.model.config.id2label:
                        predicted_label = st.session_state.model.config.id2label[str(class_id)]
            
            # If still empty, try to get from the original config file
            if not predicted_label and hasattr(st.session_state, 'model_config'):
                id2label = st.session_state.model_config.get('id2label', {})
                if str(class_id) in id2label:
                    predicted_label = id2label[str(class_id)]
            
            # If still empty, use a default
            if not predicted_label:
                predicted_label = f"Class_{class_id}"
            
            confidence_score = confidence.item()
            
            return predicted_label, confidence_score
            
        except Exception as e:
            return f"Error: {str(e)}", 0.0
    
    def parse_prediction_label(self, predicted_label):
        """Parse the prediction label into plant name, status, and disease type"""
        try:
            # Handle empty or error labels
            if not predicted_label or "Error:" in predicted_label:
                return "Unknown", "Unknown", "Unknown"
            
            # Handle class IDs like "Class_0", "Class_1", etc.
            if predicted_label.startswith("Class_"):
                try:
                    class_id = predicted_label.replace("Class_", "")
                    # Try to get the actual label from config
                    if hasattr(st.session_state, 'model_config'):
                        id2label = st.session_state.model_config.get('id2label', {})
                        if class_id in id2label:
                            actual_label = id2label[class_id]
                            # Recursively parse the actual label
                            return self.parse_prediction_label(actual_label)
                except:
                    pass
                return "Unknown", "Unknown", "Unknown"
            
            # Check if it's in the format "Plant___Disease" or "Plant___healthy"
            if "___" in predicted_label:
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
                    # Clean up disease name
                    disease_type = disease_type.replace("(Including Sour)", "").strip()
                    disease_type = disease_type.replace("(Maize)", "").strip()
                    disease_type = disease_type.replace("(Citrus Greening)", "").strip()
                    disease_type = disease_type.replace("Two Spotted Spider Mite", "Spider Mites")
                    disease_type = disease_type.replace("Gray Leaf Spot", "Gray Leaf Spot")
                
                return plant_name, status, disease_type
            
            # Try to parse other formats
            if predicted_label:
                # If it contains plant name hints
                lower_label = predicted_label.lower()
                plant_mapping = {
                    'apple': 'Apple',
                    'blueberry': 'Blueberry', 
                    'cherry': 'Cherry',
                    'corn': 'Corn',
                    'grape': 'Grape',
                    'orange': 'Orange',
                    'peach': 'Peach',
                    'pepper': 'Pepper',
                    'potato': 'Potato',
                    'raspberry': 'Raspberry',
                    'soybean': 'Soybean',
                    'squash': 'Squash',
                    'strawberry': 'Strawberry',
                    'tomato': 'Tomato'
                }
                
                for key, plant in plant_mapping.items():
                    if key in lower_label:
                        if 'healthy' in lower_label:
                            return plant, "Healthy", "None"
                        else:
                            # Extract disease name
                            disease = predicted_label.replace(key, "").replace("_", " ").strip()
                            if disease:
                                return plant, "Diseased", disease.title()
                            else:
                                return plant, "Diseased", "Unknown Disease"
            
            # Last resort: return as-is
            return "Unknown", "Unknown", predicted_label.replace("_", " ").title()
            
        except Exception as e:
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
        """Render clean sidebar with minimal navigation"""
        with st.sidebar:
            # App header with description
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <h1 style="font-size: 1.8rem; margin: 0; color: #2E8B57;">🌱 AgriEdge</h1>
                <p style="font-size: 0.9rem; color: #666; margin: 0.5rem 0 0 0;">
                    Smart Farming AI System
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Clean navigation section
            st.markdown("### 📄 Navigation")
            
            # Dashboard button
            if st.button("📊 **Dashboard**", 
                        width='stretch',
                        help="Live sensor monitoring & analytics"):
                st.switch_page("streamlit_app.py")
            
            # Disease Detection button  
            if st.button("🦠 **Disease Detection**", 
                        width='stretch',
                        help="AI-powered plant disease detection"):
                st.rerun()  # Already on disease detection page
            
            st.markdown("---")
            
            # Footer with minimal info
            st.caption("IoT Agriculture Monitoring")
    
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
            with st.expander("📋 View Disease Classes Details"):
                # Get lists from session state
                plant_types = getattr(st.session_state, 'plant_types', [])
                healthy_classes = getattr(st.session_state, 'healthy_classes', [])
                disease_classes = getattr(st.session_state, 'disease_classes', [])
                all_classes = getattr(st.session_state, 'all_classes', [])
                
                # Plant Types in one line
                st.write(f"**Plant Types ({len(plant_types)}):**")
                plant_types_str = ", ".join(plant_types)
                st.write(plant_types_str)
                
                # Healthy Classes - show all
                st.write(f"\n**Healthy Classes ({len(healthy_classes)}):**")
                healthy_str = ", ".join(healthy_classes)
                st.write(healthy_str)
                
                # Disease Classes - show disease names only
                st.write(f"\n**Disease Classes ({len(disease_classes)}):**")
                disease_names = []
                for disease in disease_classes:
                    if "___" in disease:
                        _, disease_part = disease.split("___", 1)
                        disease_name = disease_part.replace("_", " ").title()
                        disease_names.append(disease_name)
                
                disease_str = ", ".join(disease_names)
                st.write(disease_str)
                
                # Total Classes - show all
                st.write(f"\n**Total Classes ({len(all_classes)}):**")
                all_classes_str = ", ".join(all_classes)
                st.write(all_classes_str)
                
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
            
            # Load images if not already loaded
            if not st.session_state.test_images:
                test_images = self.load_test_images()
                st.session_state.test_images = test_images
            
            if not st.session_state.test_images:
                st.warning("No test images found in 'disease_detection/test_images/' folder")
                st.info("Add JPG/PNG images to the folder and refresh the page")
                return
            
            # Display images in columns
            cols = st.columns(4)
            for i, image_path in enumerate(st.session_state.test_images):
                with cols[i]:
                    try:
                        image = Image.open(image_path)
                        st.image(image, width='stretch', caption=f"Sample {i+1}")
                    except Exception:
                        st.error("Error loading image")
            
            # Run analysis button
            if st.session_state.model_loaded:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🎯 Run Disease Analysis", type="primary", width='stretch'):
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
                try:
                    image = Image.open(result['image_path'])
                    
                    # Status indicator for caption
                    if result['status'] == "Healthy":
                        status_indicator = "🟢"
                    elif result['status'] == "Diseased":
                        if result['confidence'] > 0.7:
                            status_indicator = "🔴"
                        elif result['confidence'] > 0.5:
                            status_indicator = "🟡"
                        else:
                            status_indicator = "⚫"
                    else:
                        status_indicator = "❓"
                    
                    st.image(image, width='stretch', caption=f"{status_indicator} Sample {i+1}")
                    
                    # Display prediction info with colored border
                    border_color = result['border_color']
                    st.markdown(f"""
                    <div style="border-left: 4px solid {border_color}; padding: 10px 15px; background-color: #f8f9fa; border-radius: 5px; margin: 10px 0;">
                    """, unsafe_allow_html=True)
                    
                    # Plant name
                    st.markdown(f"**🌿 Plant:** {result['plant_name']}")
                    
                    # Status
                    if result['status'] == "Healthy":
                        st.markdown("**✅ Status:** <span style='color:green;'>Healthy</span>", unsafe_allow_html=True)
                    elif result['status'] == "Diseased":
                        st.markdown("**🦠 Status:** <span style='color:red;'>Diseased</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**❓ Status:** {result['status']}")
                    
                    # Disease type (show if not "None" and not "Unknown")
                    if result['disease_type'] not in ["None", "Unknown"]:
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
                        st.progress(result['confidence'])
                    else:
                        st.markdown("**📈 Confidence:** N/A")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Error displaying result")
    
    def run(self):
        """Run the disease detection page"""

        st.markdown("""
        <style>
            div[data-testid="stSidebarNav"] {display: none;}
            section[data-testid="stSidebar"] ul {display: none !important;}
        </style>
        """, unsafe_allow_html=True)

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