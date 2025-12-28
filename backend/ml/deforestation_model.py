"""
TensorFlow-based Deforestation Detection Model
Implements change detection using Siamese CNN architecture
"""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
import numpy as np
from pathlib import Path
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class DeforestationModel:
    """Siamese CNN for detecting forest loss between image pairs"""
    
    def __init__(self, input_size: int = 256, model_path: Optional[Path] = None):
        """
        Initialize deforestation detection model
        
        Args:
            input_size: Input image size (square)
            model_path: Path to saved model weights (optional)
        """
        self.input_size = input_size
        self.model = None
        self.model_path = model_path
        
        if model_path and model_path.exists():
            self.load_model(model_path)
        else:
            self.build_model()
    
    def build_encoder(self, input_shape: Tuple[int, int, int]) -> Model:
        """
        Build the shared encoder for Siamese network
        
        Args:
            input_shape: (height, width, channels)
            
        Returns:
            Keras Model for feature extraction
        """
        inputs = keras.Input(shape=input_shape)
        
        # Encoder path (downsampling)
        x = layers.Conv2D(32, 3, padding='same', activation='relu')(inputs)
        x = layers.Conv2D(32, 3, padding='same', activation='relu')(x)
        skip1 = x
        x = layers.MaxPooling2D(2)(x)
        
        x = layers.Conv2D(64, 3, padding='same', activation='relu')(x)
        x = layers.Conv2D(64, 3, padding='same', activation='relu')(x)
        skip2 = x
        x = layers.MaxPooling2D(2)(x)
        
        x = layers.Conv2D(128, 3, padding='same', activation='relu')(x)
        x = layers.Conv2D(128, 3, padding='same', activation='relu')(x)
        skip3 = x
        x = layers.MaxPooling2D(2)(x)
        
        x = layers.Conv2D(256, 3, padding='same', activation='relu')(x)
        x = layers.Conv2D(256, 3, padding='same', activation='relu')(x)
        
        model = Model(inputs=inputs, outputs=[x, skip1, skip2, skip3], name='encoder')
        return model
    
    def build_model(self):
        """Build the complete Siamese change detection model"""
        input_shape = (self.input_size, self.input_size, 3)
        
        # Create shared encoder
        encoder = self.build_encoder(input_shape)
        
        # Define inputs for before and after images
        input_before = keras.Input(shape=input_shape, name='before')
        input_after = keras.Input(shape=input_shape, name='after')
        
        # Extract features using shared encoder
        features_before, skip1_b, skip2_b, skip3_b = encoder(input_before)
        features_after, skip1_a, skip2_a, skip3_a = encoder(input_after)
        
        # Compute difference features
        diff_features = layers.Subtract()([features_after, features_before])
        
        # Decoder path (upsampling) with skip connections from difference
        x = layers.Conv2D(256, 3, padding='same', activation='relu')(diff_features)
        x = layers.UpSampling2D(2)(x)
        
        # Concatenate with skip connection differences
        skip3_diff = layers.Subtract()([skip3_a, skip3_b])
        x = layers.Concatenate()([x, skip3_diff])
        x = layers.Conv2D(128, 3, padding='same', activation='relu')(x)
        x = layers.Conv2D(128, 3, padding='same', activation='relu')(x)
        x = layers.UpSampling2D(2)(x)
        
        skip2_diff = layers.Subtract()([skip2_a, skip2_b])
        x = layers.Concatenate()([x, skip2_diff])
        x = layers.Conv2D(64, 3, padding='same', activation='relu')(x)
        x = layers.Conv2D(64, 3, padding='same', activation='relu')(x)
        x = layers.UpSampling2D(2)(x)
        
        skip1_diff = layers.Subtract()([skip1_a, skip1_b])
        x = layers.Concatenate()([x, skip1_diff])
        x = layers.Conv2D(32, 3, padding='same', activation='relu')(x)
        x = layers.Conv2D(32, 3, padding='same', activation='relu')(x)
        
        # Output layer - probability of deforestation
        output = layers.Conv2D(1, 1, activation='sigmoid', name='deforestation_prob')(x)
        
        # Create model
        self.model = Model(
            inputs=[input_before, input_after],
            outputs=output,
            name='deforestation_detector'
        )
        
        # Compile model
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
        )
        
        logger.info("Model built successfully")
        logger.info(f"Total parameters: {self.model.count_params():,}")
    
    def predict(self, 
                before_image: np.ndarray, 
                after_image: np.ndarray,
                batch_size: int = 8) -> np.ndarray:
        """
        Predict deforestation probability map
        
        Args:
            before_image: Before image (H, W, 3) in range [0, 1]
            after_image: After image (H, W, 3) in range [0, 1]
            batch_size: Batch size for sliding window inference
            
        Returns:
            Probability map (H, W) in range [0, 1]
        """
        if self.model is None:
            raise ValueError("Model not initialized")
        
        # Get image dimensions
        h, w = before_image.shape[:2]
        
        # If images are smaller than model input, pad them
        if h < self.input_size or w < self.input_size:
            pad_h = max(0, self.input_size - h)
            pad_w = max(0, self.input_size - w)
            before_image = np.pad(before_image, ((0, pad_h), (0, pad_w), (0, 0)), mode='reflect')
            after_image = np.pad(after_image, ((0, pad_h), (0, pad_w), (0, 0)), mode='reflect')
            h, w = before_image.shape[:2]
        
        # If images are exactly the model size, predict directly
        if h == self.input_size and w == self.input_size:
            before_batch = np.expand_dims(before_image, axis=0)
            after_batch = np.expand_dims(after_image, axis=0)
            prob_map = self.model.predict([before_batch, after_batch], verbose=0)
            return prob_map[0, :, :, 0]
        
        # For larger images, use sliding window
        stride = self.input_size // 2  # 50% overlap
        prob_map = np.zeros((h, w), dtype=np.float32)
        count_map = np.zeros((h, w), dtype=np.float32)
        
        # Collect patches
        patches_before = []
        patches_after = []
        positions = []
        
        for y in range(0, h - self.input_size + 1, stride):
            for x in range(0, w - self.input_size + 1, stride):
                patch_before = before_image[y:y+self.input_size, x:x+self.input_size]
                patch_after = after_image[y:y+self.input_size, x:x+self.input_size]
                
                patches_before.append(patch_before)
                patches_after.append(patch_after)
                positions.append((y, x))
        
        # Predict in batches
        patches_before = np.array(patches_before)
        patches_after = np.array(patches_after)
        
        predictions = self.model.predict(
            [patches_before, patches_after],
            batch_size=batch_size,
            verbose=0
        )
        
        # Aggregate predictions
        for i, (y, x) in enumerate(positions):
            prob_map[y:y+self.input_size, x:x+self.input_size] += predictions[i, :, :, 0]
            count_map[y:y+self.input_size, x:x+self.input_size] += 1
        
        # Average overlapping predictions
        prob_map = np.divide(prob_map, count_map, where=count_map > 0)
        
        return prob_map
    
    def save_model(self, path: Path):
        """Save model weights"""
        if self.model is None:
            raise ValueError("No model to save")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        self.model.save(path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: Path):
        """Load model weights"""
        self.model = keras.models.load_model(path)
        logger.info(f"Model loaded from {path}")


def create_simple_change_detector():
    """
    Create a simple rule-based change detector as fallback
    Uses NDVI differencing for quick baseline results
    """
    def detect_changes(before_rgb: np.ndarray, after_rgb: np.ndarray) -> np.ndarray:
        """
        Simple change detection using color differences
        
        Args:
            before_rgb: Before image (H, W, 3)
            after_rgb: After image (H, W, 3)
            
        Returns:
            Change probability map (H, W)
        """
        # Calculate vegetation index approximation from RGB
        # Green - Red as proxy for vegetation
        def vegetation_index(rgb):
            green = rgb[:, :, 1].astype(np.float32)
            red = rgb[:, :, 0].astype(np.float32)
            return (green - red) / (green + red + 1e-8)
        
        vi_before = vegetation_index(before_rgb)
        vi_after = vegetation_index(after_rgb)
        
        # Calculate change (negative = vegetation loss)
        change = vi_after - vi_before
        
        # Convert to probability (more negative = higher deforestation probability)
        prob = np.clip(-change * 2, 0, 1)
        
        # Apply some smoothing
        from scipy.ndimage import gaussian_filter
        prob = gaussian_filter(prob, sigma=2)
        
        return prob
    
    return detect_changes


if __name__ == "__main__":
    # Test model creation
    logging.basicConfig(level=logging.INFO)
    
    model = DeforestationModel(input_size=256)
    print(model.model.summary())
    
    # Test prediction with random data
    test_before = np.random.rand(256, 256, 3).astype(np.float32)
    test_after = np.random.rand(256, 256, 3).astype(np.float32)
    
    prob_map = model.predict(test_before, test_after)
    print(f"Probability map shape: {prob_map.shape}")
    print(f"Probability range: [{prob_map.min():.3f}, {prob_map.max():.3f}]")
