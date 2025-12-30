"""
Spheroid Image Processing Module
Analyzes spheroid images to identify background, border, and core regions.
"""

import cv2
import numpy as np
from typing import Tuple, Dict


class SpheroidProcessor:
    """Process spheroid images to identify core, border, and background regions."""
    
    def __init__(self):
        self.original_image = None
        self.gray_image = None
        self.enhanced_image = None
        self.results = {}
        
    def load_image(self, image_path: str) -> bool:
        """Load an image from file path."""
        try:
            self.original_image = cv2.imread(image_path)
            if self.original_image is None:
                return False
            
            # Convert to grayscale if needed
            if len(self.original_image.shape) == 3:
                self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            else:
                self.gray_image = self.original_image.copy()
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def process_spheroid(self, 
                        denoise_strength: int = 10,
                        contrast_clip: float = 2.0,
                        normalize_contrast: bool = True,
                        use_clahe: bool = True,
                        edge_sensitivity: int = 0,
                        threshold_value: int = 127,
                        morphology_size: int = 5,
                        core_percentile: int = 50,
                        min_area: int = 100,
                        crop_bounds: tuple = None) -> Dict:
        """
        Process the spheroid image to identify core, border, and background.
        
        Algorithm:
        1. Denoise the image
        2. Normalize/extremize contrast (map actual range to 0-255)
        3. Apply local or global contrast enhancement
        4. Invert if needed (spheroid should be white on black)
        5. Remove background (threshold + morphology)
        6. Define core (darker pixels within spheroid) and border (lighter pixels)
        
        Args:
            denoise_strength: Strength of denoising (1-20, higher = more smoothing)
            contrast_clip: CLAHE clip limit for local contrast enhancement
            normalize_contrast: If True, stretch histogram to use full 0-255 range
            use_clahe: If True, use local (CLAHE) contrast; if False, use global
            edge_sensitivity: Canny edge detection threshold (0=off, higher=more sensitive)
            threshold_value: Threshold for background removal (manual value)
            morphology_size: Kernel size for morphological operations (fills gaps/smooths edges)
            core_percentile: Percentile for core definition (0-100, lower = smaller darker core)
            min_area: Minimum contour area to keep (filters noise)
            crop_bounds: Tuple (h_start%, h_end%, v_start%, v_end%) to restrict analysis region
            
        Returns:
            Dictionary containing processed images and metrics
        """
        if self.gray_image is None:
            return {}
        
        # STEP 0: Apply crop if specified
        if crop_bounds:
            h_start, h_end, v_start, v_end = crop_bounds
            h, w = self.gray_image.shape
            
            # Validate crop bounds
            if h_start >= h_end or v_start >= v_end:
                # Invalid crop, use full image
                gray_working = self.gray_image
            else:
                # Convert percentages to pixels
                x1 = int(w * h_start / 100)
                x2 = int(w * h_end / 100)
                y1 = int(h * v_start / 100)
                y2 = int(h * v_end / 100)
                
                # Ensure valid range
                x1 = max(0, min(x1, w-1))
                x2 = max(x1+1, min(x2, w))
                y1 = max(0, min(y1, h-1))
                y2 = max(y1+1, min(y2, h))
                
                # Crop the working image
                gray_working = self.gray_image[y1:y2, x1:x2].copy()
                
                # Store crop offset for later use
                self.crop_offset = (x1, y1)
        else:
            gray_working = self.gray_image
            self.crop_offset = (0, 0)
        
        # STEP 1: Denoise the image
        denoised = cv2.fastNlMeansDenoising(gray_working, None, 
                                           h=denoise_strength, 
                                           templateWindowSize=7, 
                                           searchWindowSize=21)
        
        # STEP 2: Normalize contrast - extremize the actual intensity range
        if normalize_contrast:
            # Find actual min/max values in the image
            min_val = denoised.min()
            max_val = denoised.max()
            
            if max_val > min_val:
                # Stretch to full 0-255 range
                normalized = ((denoised - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            else:
                normalized = denoised
        else:
            normalized = denoised
        
        # STEP 2b: Apply contrast enhancement
        if use_clahe:
            # Local contrast enhancement using CLAHE
            # Good for images with varying local contrast
            clahe = cv2.createCLAHE(clipLimit=contrast_clip, tileGridSize=(8,8))
            enhanced = clahe.apply(normalized)
        else:
            # Global contrast enhancement
            # Simple but effective for uniform images
            enhanced = normalized
        
        # STEP 3: Detect if spheroid is dark on light background
        # Check mean intensity - if background is light, most pixels will be bright
        mean_intensity = enhanced.mean()
        
        # If mean is > 127, background is light, so spheroid is dark - need to invert
        if mean_intensity > 127:
            enhanced = 255 - enhanced
        
        self.enhanced_image = enhanced
        
        # STEP 3.5: Optional edge detection for subtle borders
        if edge_sensitivity > 0:
            # Use Canny edge detection to find faint borders
            edges = cv2.Canny(enhanced, edge_sensitivity, edge_sensitivity * 2)
            # Dilate edges to make them thicker
            kernel_edge = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel_edge, iterations=1)
            # Combine edges with enhanced image
            enhanced = cv2.add(enhanced, edges)
        
        # STEP 4: Remove background using threshold
        _, binary = cv2.threshold(enhanced, threshold_value, 255, cv2.THRESH_BINARY)
        
        # Clean up the binary mask with morphological operations
        kernel_size = morphology_size
        kernel_small = np.ones((3, 3), np.uint8)
        kernel_large = np.ones((kernel_size, kernel_size), np.uint8)
        
        # Remove small noise
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_small, iterations=2)
        # Fill holes and smooth edges - now adjustable
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_large, iterations=2)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_large, iterations=2)
        
        # STEP 5: Find the main spheroid contour
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return self._create_empty_results()
        
        # Filter by minimum area and select the largest
        valid_contours = [c for c in contours if cv2.contourArea(c) >= min_area]
        
        if not valid_contours:
            return self._create_empty_results()
        
        # Get the largest contour (main spheroid)
        main_contour = max(valid_contours, key=cv2.contourArea)
        
        # Create clean spheroid mask
        spheroid_mask = np.zeros_like(binary)
        cv2.drawContours(spheroid_mask, [main_contour], -1, 255, -1)
        
        # STEP 6: Define core and border using ORIGINAL intensity only (core = darker pixels)
        # Use original grayscale (or cropped version if crop was applied), not enhanced/inverted
        # Need to get the original intensity values from the working image (which may be cropped)
        if crop_bounds:
            # Use the cropped version
            gray_for_core = gray_working
        else:
            # Use full original
            gray_for_core = self.gray_image
        
        spheroid_pixels_original = gray_for_core[spheroid_mask > 0]
        
        if len(spheroid_pixels_original) == 0:
            return self._create_empty_results()
        
        # Find the threshold intensity for the core based on original darkness
        # Lower percentile = darker pixels = core
        core_threshold = np.percentile(spheroid_pixels_original, core_percentile)
        
        # Core = darkest pixels in original image (below threshold)
        core_mask_raw = np.zeros_like(spheroid_mask)
        core_mask_raw[(spheroid_mask > 0) & (gray_for_core < core_threshold)] = 255
        
        # Smooth with morphological operations
        kernel_smooth = np.ones((5, 5), np.uint8)
        core_mask_smoothed = cv2.morphologyEx(core_mask_raw, cv2.MORPH_OPEN, kernel_smooth, iterations=1)
        core_mask_smoothed = cv2.morphologyEx(core_mask_smoothed, cv2.MORPH_CLOSE, kernel_smooth, iterations=1)
        
        # Keep only the LARGEST connected component (core must be single component)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(core_mask_smoothed, connectivity=8)
        
        core_mask = np.zeros_like(spheroid_mask)
        if num_labels > 1:  # 0 is background, so we need at least 2 labels
            # Find largest component (excluding background label 0)
            largest_component = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            core_mask[labels == largest_component] = 255
        
        # Ensure core is within spheroid
        core_mask = cv2.bitwise_and(core_mask, spheroid_mask)
        
        # Border = spheroid pixels not in core
        border_mask = cv2.subtract(spheroid_mask, core_mask)
        
        # If cropped, place masks back on full-sized canvas at correct position
        if crop_bounds:
            h_start, h_end, v_start, v_end = crop_bounds
            h, w = self.gray_image.shape
            x_offset = int(w * h_start / 100)
            y_offset = int(h * v_start / 100)
            
            # Create full-sized masks
            full_spheroid_mask = np.zeros_like(self.gray_image)
            full_core_mask = np.zeros_like(self.gray_image)
            full_border_mask = np.zeros_like(self.gray_image)
            
            # Place cropped masks at correct position
            crop_h, crop_w = spheroid_mask.shape
            full_spheroid_mask[y_offset:y_offset+crop_h, x_offset:x_offset+crop_w] = spheroid_mask
            full_core_mask[y_offset:y_offset+crop_h, x_offset:x_offset+crop_w] = core_mask
            full_border_mask[y_offset:y_offset+crop_h, x_offset:x_offset+crop_w] = border_mask
            
            # Use full-sized masks for output
            binary_output = full_spheroid_mask
            core_mask_out = full_core_mask
            border_mask_out = full_border_mask
        else:
            # No crop, use as-is
            binary_output = spheroid_mask.copy()
            core_mask_out = core_mask
            border_mask_out = border_mask
        
        # Create colored overlay
        # Pass the working image and crop offset for proper positioning
        overlay = self._create_overlay(core_mask, border_mask, gray_working, crop_bounds)
        
        # Count pixels
        core_pixels = np.count_nonzero(core_mask)
        border_pixels = np.count_nonzero(border_mask)
        total_spheroid_pixels = core_pixels + border_pixels
        
        self.results = {
            'binary_output': binary_output,
            'overlay': overlay,
            'core_mask': core_mask_out,
            'border_mask': border_mask_out,
            'spheroid_mask': binary_output,
            'core_pixels': core_pixels,
            'border_pixels': border_pixels,
            'total_pixels': total_spheroid_pixels,
            'enhanced_image': enhanced
        }
        
        return self.results
    
    def _create_empty_results(self) -> Dict:
        """Create empty results when no spheroid is detected."""
        empty = np.zeros_like(self.gray_image)
        return {
            'binary_output': empty,
            'overlay': self.original_image.copy() if self.original_image is not None else empty,
            'core_mask': empty,
            'border_mask': empty,
            'spheroid_mask': empty,
            'core_pixels': 0,
            'border_pixels': 0,
            'total_pixels': 0
        }
    
    def _create_overlay(self, core_mask: np.ndarray, border_mask: np.ndarray, working_image: np.ndarray = None, crop_bounds = None) -> np.ndarray:
        """Create colored overlay showing ONLY outlines: core (yellow line) and border (red line)."""
        # Start with full original image
        if self.original_image is None:
            return np.zeros((core_mask.shape[0], core_mask.shape[1], 3), dtype=np.uint8)
        
        if len(self.original_image.shape) == 2:
            overlay = cv2.cvtColor(self.original_image, cv2.COLOR_GRAY2BGR)
        else:
            overlay = self.original_image.copy()
        
        # Calculate offset if cropped
        x_offset, y_offset = 0, 0
        if crop_bounds:
            h_start, h_end, v_start, v_end = crop_bounds
            h, w = self.original_image.shape[:2]
            x_offset = int(w * h_start / 100)
            y_offset = int(h * v_start / 100)
        
        # Draw border outer edge as RED OUTLINE
        if np.any(border_mask > 0):
            # Find all contours of the entire spheroid (border + core)
            # This gives us the outer edge
            full_spheroid = cv2.bitwise_or(border_mask, core_mask)
            outer_contours, _ = cv2.findContours(full_spheroid.copy(), cv2.RETR_EXTERNAL, 
                                                 cv2.CHAIN_APPROX_SIMPLE)
            # Apply offset to contours if cropped
            if x_offset != 0 or y_offset != 0:
                outer_contours = [cnt + np.array([x_offset, y_offset]) for cnt in outer_contours]
            cv2.drawContours(overlay, outer_contours, -1, (0, 0, 255), thickness=2)
        
        # Draw core outline as YELLOW LINE
        if np.any(core_mask > 0):
            core_contours, _ = cv2.findContours(core_mask.copy(), cv2.RETR_EXTERNAL, 
                                               cv2.CHAIN_APPROX_SIMPLE)
            # Apply offset to contours if cropped
            if x_offset != 0 or y_offset != 0:
                core_contours = [cnt + np.array([x_offset, y_offset]) for cnt in core_contours]
            cv2.drawContours(overlay, core_contours, -1, (0, 255, 255), thickness=2)
        
        return overlay
    
    def save_outputs(self, output_dir: str, base_name: str = "spheroid"):
        """Save all output images to directory."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        if 'binary_output' in self.results:
            cv2.imwrite(os.path.join(output_dir, f"{base_name}_binary.png"), 
                       self.results['binary_output'])
        
        if 'overlay' in self.results:
            cv2.imwrite(os.path.join(output_dir, f"{base_name}_overlay.png"), 
                       self.results['overlay'])
