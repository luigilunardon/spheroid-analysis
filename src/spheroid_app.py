"""
Spheroid Analysis Application - User-friendly GUI
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from spheroid_processor import SpheroidProcessor
import os


# Parameter tooltips
TOOLTIPS = {
    'denoise': 'Smooths the image to reduce graininess.\nHigher values create smoother results.\n+/- buttons: ±0.5',
    'contrast': 'Adjusts image contrast using CLAHE.\nBelow 1.0 = flatten, above 1.0 = sharpen.\n+/- buttons: ±0.05',
    'edge_detect': 'Enhances faint borders using edge detection.\nHigher = detects fainter edges.\n+/- buttons: ±1',
    'threshold': 'Separates spheroid from background.\nAdjust until spheroid is fully captured.\n+/- buttons: ±0.5',
    'morphology': 'Fills gaps in spheroid border.\nHigher = fills larger holes and smooths edges.\n+/- buttons: ±1',
    'core_size': 'Controls how much of darkest region is core.\nHigher percentage = larger core.\n+/- buttons: ±0.5%',
    'min_area': 'Ignores small specks and noise (pixels).\nIncrease if seeing unwanted dots.\n+/- buttons: ±10'
}


class SpheroidApp(ctk.CTk):
    """Main application window for spheroid analysis."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Spheroid Analysis")
        self.geometry("1400x900")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize processor
        self.processor = SpheroidProcessor()
        self.current_image_path = None
        
        # Tooltip tracking
        self.tooltip_window = None
        
        # Setup UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel - Controls
        self.controls_frame = ctk.CTkFrame(self, width=300, corner_radius=10)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Right panel - Image display
        self.display_frame = ctk.CTkFrame(self, corner_radius=10)
        self.display_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self._setup_controls()
        self._setup_display()
        
    def _setup_controls(self):
        """Setup control panel with buttons and sliders."""
        # Title
        # Load and Save buttons in same row
        buttons_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        buttons_frame.pack(pady=10, padx=20, fill="x")
        
        self.load_btn = ctk.CTkButton(buttons_frame, text="Load", 
                                      command=self.load_image,
                                      height=30, font=ctk.CTkFont(size=11))
        self.load_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.save_btn = ctk.CTkButton(buttons_frame, text="Save", 
                                     command=self.save_results,
                                     height=30, font=ctk.CTkFont(size=11),
                                     state="disabled")
        self.save_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Parameters Section
        params_label = ctk.CTkLabel(self.controls_frame, text="Parameters", 
                                   font=ctk.CTkFont(size=14, weight="bold"))
        params_label.pack(pady=(12, 5), padx=20)
        
        # Crop controls with dual sliders
        self._create_crop_control(
            label_text="Horizontal Crop",
            tooltip_text="Crops image horizontally (% from edges).\nLeft/Right values exclude outer regions.\n+/- buttons: ±1%",
            var_name='h_crop'
        )
        
        self._create_crop_control(
            label_text="Vertical Crop",
            tooltip_text="Crops image vertically (% from edges).\nBottom/Top values exclude outer regions.\n+/- buttons: ±1%",
            var_name='v_crop'
        )
        
        # Denoise with +/- buttons and tooltip
        self._create_param_control(
            label_text="Denoise Strength: 10",
            slider_from=1, slider_to=20, default=10,
            step=0.5, tooltip_key='denoise',
            var_name='denoise'
        )
        
        # Contrast Enhancement
        self._create_param_control(
            label_text="Contrast: 2.0",
            slider_from=0.1, slider_to=10.0, default=2.0,
            step=0.05, tooltip_key='contrast',
            var_name='contrast'
        )
        
        # Edge Detection Sensitivity
        self._create_param_control(
            label_text="Edge Sensitivity: 0",
            slider_from=0, slider_to=100, default=0,
            step=1, tooltip_key='edge_detect',
            var_name='edge'
        )
        
        # Threshold
        self._create_param_control(
            label_text="Threshold: 127",
            slider_from=0, slider_to=255, default=127,
            step=0.5, tooltip_key='threshold',
            var_name='thresh'
        )
        
        # Morphology Size
        self._create_param_control(
            label_text="Border Fill: 5",
            slider_from=1, slider_to=15, default=5,
            step=1, tooltip_key='morphology',
            var_name='morph'
        )
        
        # Core Size
        self._create_param_control(
            label_text="Core Size: 50%",
            slider_from=1, slider_to=99, default=50,
            step=0.5, tooltip_key='core_size',
            var_name='core'
        )
        
        # Minimum Area slider
        self._create_param_control(
            label_text="Min Area: 100",
            slider_from=10, slider_to=1000, default=100,
            step=10, tooltip_key='min_area',
            var_name='area'
        )
        
        # Results Section
        results_label = ctk.CTkLabel(self.controls_frame, text="Results", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        results_label.pack(pady=(12, 5), padx=20)
        
        # Pixel counts on one line
        self.pixel_count_label = ctk.CTkLabel(self.controls_frame, 
                                             text="Pixel count - Core: 0  Border: 0  Total: 0",
                                             font=ctk.CTkFont(size=11))
        self.pixel_count_label.pack(pady=2, padx=20, anchor="w")
    
    def _create_param_control(self, label_text, slider_from, slider_to, default, step, tooltip_key, var_name):
        """Create a parameter control with label, slider, +/- buttons, and tooltip."""
        # Create frame for this parameter
        param_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        param_frame.pack(pady=(4, 0), padx=20, fill="x")
        
        # Label with tooltip button
        label_frame = ctk.CTkFrame(param_frame, fg_color="transparent")
        label_frame.pack(fill="x")
        
        # Extract parameter name only (no value)
        parts = label_text.rsplit(': ', 1)
        label_name = parts[0] if len(parts) > 1 else label_text
        
        # Create label with inline info icon (no value)
        full_text = f"{label_name} ⓘ"
        label = ctk.CTkLabel(label_frame, text=full_text, anchor="w")
        label.pack(side="left")
        
        # Bind hover to show tooltip
        label.bind("<Enter>", lambda e: self._show_tooltip(e, tooltip_key))
        label.bind("<Leave>", lambda e: self._hide_tooltip())
        
        # Store label reference
        setattr(self, f"{var_name}_label", label)
        
        # Slider with +/- buttons frame
        slider_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        slider_frame.pack(pady=(0, 5), padx=20, fill="x")
        
        # Minus button
        minus_btn = ctk.CTkButton(slider_frame, text="−", width=26,
                                 command=lambda: self._adjust_slider(var_name, -step))
        minus_btn.pack(side="left", padx=(0, 3))
        
        # Slider
        slider = ctk.CTkSlider(slider_frame, from_=slider_from, to=slider_to,
                              command=self.on_parameter_change)
        slider.set(default)
        slider.pack(side="left", fill="x", expand=True, padx=(0, 3))
        
        # Plus button
        plus_btn = ctk.CTkButton(slider_frame, text="+", width=26,
                                command=lambda: self._adjust_slider(var_name, step))
        plus_btn.pack(side="left")
        
        # Entry box for direct input
        entry = ctk.CTkEntry(slider_frame, width=60)
        entry.insert(0, str(default))
        entry.bind("<Return>", lambda e: self._set_slider_from_entry(var_name, entry, slider_from, slider_to))
        entry.pack(side="left", padx=(3, 0))
        
        # Store slider and entry references
        setattr(self, f"{var_name}_slider", slider)
        setattr(self, f"{var_name}_entry", entry)
    
    def _create_crop_control(self, label_text, tooltip_text, var_name):
        """Create a dual-slider crop control with left/down and right/up values."""
        # Create frame for this parameter
        param_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        param_frame.pack(pady=(4, 0), padx=20, fill="x")
        
        # Label with tooltip
        label_frame = ctk.CTkFrame(param_frame, fg_color="transparent")
        label_frame.pack(fill="x")
        
        label = ctk.CTkLabel(label_frame, text=f"{label_text} ⓘ", anchor="w")
        label.pack(side="left")
        
        # Bind hover to show custom tooltip
        label.bind("<Enter>", lambda e: self._show_custom_tooltip(e, tooltip_text))
        label.bind("<Leave>", lambda e: self._hide_tooltip())
        
        # Store label reference
        setattr(self, f"{var_name}_label", label)
        
        # Dual slider frame (left/down and right/up)
        slider_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        slider_frame.pack(pady=(0, 5), padx=20, fill="x")
        
        # Left/Down value entry
        left_entry = ctk.CTkEntry(slider_frame, width=80)
        left_entry.insert(0, "0")
        left_entry.bind("<Return>", lambda e: self.on_crop_change())
        left_entry.bind("<FocusOut>", lambda e: self.on_crop_change())
        left_entry.pack(side="left", padx=(0, 20))
        
        # Right/Up value entry
        right_entry = ctk.CTkEntry(slider_frame, width=80)
        right_entry.insert(0, "100")
        right_entry.bind("<Return>", lambda e: self.on_crop_change())
        right_entry.bind("<FocusOut>", lambda e: self.on_crop_change())
        right_entry.pack(side="left")
        
        # Store entry references only
        setattr(self, f"{var_name}_left_entry", left_entry)
        setattr(self, f"{var_name}_right_entry", right_entry)
    
    def _create_tooltip_button(self, parent, tooltip_key):
        """Create a small ? button that shows tooltip on hover."""
        btn = ctk.CTkButton(parent, text="?", width=18, height=18,
                           font=ctk.CTkFont(size=11, weight="bold"),
                           fg_color="gray40", hover_color="gray30")
        
        # Bind hover events
        btn.bind("<Enter>", lambda e: self._show_tooltip(e, tooltip_key))
        btn.bind("<Leave>", lambda e: self._hide_tooltip())
        
        return btn
    
    def _show_tooltip(self, event, tooltip_key):
        """Show tooltip window."""
        if tooltip_key not in TOOLTIPS:
            return
        
        # Create tooltip window
        self.tooltip_window = ctk.CTkToplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        
        # Position near cursor
        x = event.x_root + 10
        y = event.y_root + 10
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Add text
        label = ctk.CTkLabel(self.tooltip_window, text=TOOLTIPS[tooltip_key],
                            justify="left", padx=10, pady=5,
                            corner_radius=5)
        label.pack()
    
    def _show_custom_tooltip(self, event, tooltip_text):
        """Show custom tooltip window with custom text."""
        # Create tooltip window
        self.tooltip_window = ctk.CTkToplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        
        # Position near cursor
        x = event.x_root + 10
        y = event.y_root + 10
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Add text
        label = ctk.CTkLabel(self.tooltip_window, text=tooltip_text,
                            justify="left", padx=10, pady=5,
                            corner_radius=5)
        label.pack()
    
    def _hide_tooltip(self):
        """Hide tooltip window."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def _adjust_slider(self, var_name, delta):
        """Adjust slider value by delta amount."""
        slider = getattr(self, f"{var_name}_slider")
        entry = getattr(self, f"{var_name}_entry")
        current = slider.get()
        new_value = current + delta
        
        # Clamp to slider range
        new_value = max(slider.cget("from_"), min(slider.cget("to"), new_value))
        
        slider.set(new_value)
        entry.delete(0, "end")
        entry.insert(0, f"{new_value:.1f}" if isinstance(new_value, float) else str(int(new_value)))
        self.on_parameter_change(new_value)
    
    def _set_slider_from_entry(self, var_name, entry, min_val, max_val):
        """Set slider value from entry box input."""
        try:
            value = float(entry.get())
            # Clamp to valid range
            value = max(min_val, min(max_val, value))
            
            slider = getattr(self, f"{var_name}_slider")
            slider.set(value)
            
            # Update entry to show clamped value
            entry.delete(0, "end")
            entry.insert(0, f"{value:.1f}" if isinstance(value, float) else str(int(value)))
            
            self.on_parameter_change(value)
        except ValueError:
            # Invalid input, reset to current slider value
            slider = getattr(self, f"{var_name}_slider")
            current = slider.get()
            entry.delete(0, "end")
            entry.insert(0, f"{current:.1f}" if isinstance(current, float) else str(int(current)))
    
    def _set_slider_from_entry(self, var_name, entry, min_val, max_val):
        """Set slider value from entry box input."""
        try:
            value = float(entry.get())
            # Clamp to valid range
            value = max(min_val, min(max_val, value))
            
            slider = getattr(self, f"{var_name}_slider")
            slider.set(value)
            
            # Update entry to show clamped value
            entry.delete(0, "end")
            entry.insert(0, f"{value:.1f}" if isinstance(value, float) else str(int(value)))
            
            self.on_parameter_change(value)
        except ValueError:
            # Invalid input, reset to current slider value
            slider = getattr(self, f"{var_name}_slider")
            current = slider.get()
            entry.delete(0, "end")
            entry.insert(0, f"{current:.1f}" if isinstance(current, float) else str(int(current)))
        
    def _setup_display(self):
        """Setup image display area."""
        # Configure grid for display frame
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_columnconfigure(1, weight=1)
        self.display_frame.grid_rowconfigure(1, weight=1)
        
        # View selector
        self.view_selector = ctk.CTkSegmentedButton(
            self.display_frame,
            values=["Overlay", "Binary"],
            command=self.change_view
        )
        self.view_selector.set("Overlay")
        self.view_selector.grid(row=0, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        
        # Image canvas - left
        self.canvas_frame_left = ctk.CTkFrame(self.display_frame)
        self.canvas_frame_left.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.image_label_left = ctk.CTkLabel(self.canvas_frame_left, text="No image loaded",
                                            font=ctk.CTkFont(size=16))
        self.image_label_left.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Image canvas - right
        self.canvas_frame_right = ctk.CTkFrame(self.display_frame)
        self.canvas_frame_right.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        self.image_label_right = ctk.CTkLabel(self.canvas_frame_right, text="Process image to see results",
                                             font=ctk.CTkFont(size=16))
        self.image_label_right.pack(expand=True, fill="both", padx=20, pady=20)
        
    def load_image(self):
        """Load an image file."""
        file_path = filedialog.askopenfilename(
            title="Select Spheroid Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.tif *.tiff *.bmp"),
                      ("All files", "*.*")]
        )
        
        if file_path:
            if self.processor.load_image(file_path):
                self.current_image_path = file_path
                # Reset crop entries to no crop
                self.h_crop_left_entry.delete(0, 'end')
                self.h_crop_left_entry.insert(0, '0')
                self.h_crop_right_entry.delete(0, 'end')
                self.h_crop_right_entry.insert(0, '100')
                self.v_crop_left_entry.delete(0, 'end')
                self.v_crop_left_entry.insert(0, '0')
                self.v_crop_right_entry.delete(0, 'end')
                self.v_crop_right_entry.insert(0, '100')
                self.display_original_image()
                self.process_image()
            else:
                messagebox.showerror("Error", "Failed to load image.")
    
    def on_crop_change(self, value=None):
        """Handle crop entry changes."""
        # Update original image display with shading
        self.display_original_image()
        
        # Trigger reprocessing
        self.process_image()
    
    def display_original_image(self):
        """Display the loaded original image with crop shading."""
        if self.processor.original_image is not None:
            image = self.processor.original_image.copy()
            
            # Add semi-transparent shading for cropped-out areas
            try:
                h_start = float(self.h_crop_left_entry.get())
                h_end = float(self.h_crop_right_entry.get())
                v_start = float(self.v_crop_left_entry.get())
                v_end = float(self.v_crop_right_entry.get())
            except (ValueError, AttributeError):
                # Default to no crop if entries have invalid values
                h_start, h_end, v_start, v_end = 0, 100, 0, 100
            
            if h_start > 0 or h_end < 100 or v_start > 0 or v_end < 100:
                # Create overlay for cropped regions
                overlay = image.copy()
                h, w = image.shape[:2]
                
                # Calculate pixel boundaries
                h_start_px = int(w * h_start / 100)
                h_end_px = int(w * h_end / 100)
                v_start_px = int(h * v_start / 100)
                v_end_px = int(h * v_end / 100)
                
                # Darken cropped-out regions (50% darker)
                overlay[:, :h_start_px] = overlay[:, :h_start_px] // 2  # Left
                overlay[:, h_end_px:] = overlay[:, h_end_px:] // 2  # Right
                overlay[:v_start_px, :] = overlay[:v_start_px, :] // 2  # Top
                overlay[v_end_px:, :] = overlay[v_end_px:, :] // 2  # Bottom
                
                image = overlay
            
            self._display_cv_image(image, self.image_label_left)
    
    def on_parameter_change(self, value=None):
        """Handle parameter slider changes."""
        # Update labels and entry boxes
        denoise_val = self.denoise_slider.get()
        self.denoise_label.configure(text=f"Denoise Strength ⓘ: {denoise_val:.1f}")
        self.denoise_entry.delete(0, "end")
        self.denoise_entry.insert(0, f"{denoise_val:.1f}")
        
        contrast_val = self.contrast_slider.get()
        self.contrast_label.configure(text=f"Contrast ⓘ: {contrast_val:.2f}")
        self.contrast_entry.delete(0, "end")
        self.contrast_entry.insert(0, f"{contrast_val:.2f}")
        
        edge_val = self.edge_slider.get()
        self.edge_label.configure(text=f"Edge Sensitivity ⓘ: {int(edge_val)}")
        self.edge_entry.delete(0, "end")
        self.edge_entry.insert(0, str(int(edge_val)))
        
        thresh_val = self.thresh_slider.get()
        self.thresh_label.configure(text=f"Threshold ⓘ: {int(thresh_val)}")
        self.thresh_entry.delete(0, "end")
        self.thresh_entry.insert(0, str(int(thresh_val)))
        
        morph_val = self.morph_slider.get()
        self.morph_label.configure(text=f"Border Fill ⓘ: {int(morph_val)}")
        self.morph_entry.delete(0, "end")
        self.morph_entry.insert(0, str(int(morph_val)))
        
        core_val = self.core_slider.get()
        self.core_label.configure(text=f"Core Size ⓘ: {core_val:.1f}%")
        self.core_entry.delete(0, "end")
        self.core_entry.insert(0, f"{core_val:.1f}")
        
        area_val = self.area_slider.get()
        self.area_label.configure(text=f"Min Area ⓘ: {int(area_val)}")
        self.area_entry.delete(0, "end")
        self.area_entry.insert(0, str(int(area_val)))
        
        # Reprocess image if one is loaded
        if self.processor.original_image is not None:
            self.process_image()
    
    def process_image(self):
        """Process the loaded image with current parameters."""
        if self.processor.original_image is None:
            return
        
        # Get parameters
        denoise = int(self.denoise_slider.get())
        contrast = self.contrast_slider.get()
        edge_sensitivity = int(self.edge_slider.get())
        thresh = int(self.thresh_slider.get())
        morph_size = int(self.morph_slider.get())
        core_percentile = int(self.core_slider.get())
        min_area = int(self.area_slider.get())
        
        # Get crop bounds from entries (h_start, h_end, v_start, v_end)
        try:
            h_start = float(self.h_crop_left_entry.get())
            h_end = float(self.h_crop_right_entry.get())
            v_start = float(self.v_crop_left_entry.get())
            v_end = float(self.v_crop_right_entry.get())
        except (ValueError, AttributeError):
            # Default to no crop if entries have invalid values
            h_start, h_end, v_start, v_end = 0, 100, 0, 100
        
        # Only use crop if bounds are not default (0, 100, 0, 100)
        crop_bounds = None
        if h_start > 0 or h_end < 100 or v_start > 0 or v_end < 100:
            crop_bounds = (h_start, h_end, v_start, v_end)
        
        # Process the image (always use CLAHE and normalize)
        results = self.processor.process_spheroid(
            denoise_strength=denoise,
            contrast_clip=contrast,
            normalize_contrast=True,
            use_clahe=True,
            edge_sensitivity=edge_sensitivity,
            threshold_value=thresh,
            morphology_size=morph_size,
            core_percentile=core_percentile,
            min_area=min_area,
            crop_bounds=crop_bounds
        )
        
        # Update display
        if results:
            self.update_results_display(results)
            self.change_view(self.view_selector.get())
            self.save_btn.configure(state="normal")
    
    def update_results_display(self, results):
        """Update pixel count label."""
        self.pixel_count_label.configure(
            text=f"Pixel count - Core: {results['core_pixels']:,}  Border: {results['border_pixels']:,}  Total: {results['total_pixels']:,}"
        )
    
    def change_view(self, view_name):
        """Change the displayed view."""
        if not self.processor.results:
            return
        
        if view_name == "Overlay":
            self._display_cv_image(self.processor.results['overlay'], self.image_label_right)
        elif view_name == "Binary":
            self._display_cv_image(self.processor.results['binary_output'], self.image_label_right)
        
        # Force update
        self.image_label_right.update_idletasks()
    
    def _display_cv_image(self, cv_image, label_widget, max_size=(500, 500)):
        """Display OpenCV image in a tkinter label."""
        if cv_image is None:
            return
        
        # Convert BGR to RGB if needed
        if len(cv_image.shape) == 3:
            display_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        else:
            display_image = cv_image
        
        # Convert to PIL Image
        pil_image = Image.fromarray(display_image)
        
        # Resize to fit display
        pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to CTkImage to avoid warning
        ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, 
                                  size=pil_image.size)
        
        # Update label
        label_widget.configure(image=ctk_image, text="")
        label_widget.image = ctk_image  # Keep a reference
        label_widget.update_idletasks()  # Force update
    
    def save_results(self):
        """Save processed results."""
        if not self.processor.results:
            messagebox.showwarning("Warning", "No results to save. Process an image first.")
            return
        
        # Ask for output directory
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        
        if output_dir:
            try:
                # Get base name from input file
                if self.current_image_path:
                    base_name = os.path.splitext(os.path.basename(self.current_image_path))[0]
                else:
                    base_name = "spheroid"
                
                # Save images
                self.processor.save_outputs(output_dir, base_name)
                
                # Save text file with metrics
                metrics_file = os.path.join(output_dir, f"{base_name}_metrics.txt")
                with open(metrics_file, 'w') as f:
                    f.write(f"Spheroid Analysis Results\n")
                    f.write(f"={'='*50}\n\n")
                    f.write(f"Input Image: {self.current_image_path}\n\n")
                    f.write(f"Parameters:\n")
                    f.write(f"  Denoise Strength: {int(self.denoise_slider.get())}\n")
                    f.write(f"  Contrast: {self.contrast_slider.get():.2f}\n")
                    f.write(f"  Edge Sensitivity: {int(self.edge_slider.get())}\n")
                    f.write(f"  Threshold: {int(self.thresh_slider.get())}\n")
                    f.write(f"  Border Fill: {int(self.morph_slider.get())}\n")
                    f.write(f"  Core Size: {int(self.core_slider.get())}%\n")
                    f.write(f"  Min Area: {int(self.area_slider.get())}\n\n")
                    f.write(f"Results:\n")
                    f.write(f"  Core Pixels: {self.processor.results['core_pixels']:,}\n")
                    f.write(f"  Border Pixels: {self.processor.results['border_pixels']:,}\n")
                    f.write(f"  Total Spheroid Pixels: {self.processor.results['total_pixels']:,}\n")
                
                messagebox.showinfo("Success", f"Results saved to:\n{output_dir}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save results:\n{str(e)}")


def main():
    """Main entry point."""
    app = SpheroidApp()
    app.mainloop()


if __name__ == "__main__":
    main()
