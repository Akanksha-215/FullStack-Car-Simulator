# import cv2
# import numpy as np

# def draw_lane_lines(img, left_line, right_line, color=(0, 255, 0), thickness=8):
#     """
#     Draws lane lines on an image with improved visualization.
#     """
#     line_img = np.zeros_like(img)
    
#     if left_line is not None:
#         cv2.line(line_img, (left_line[0], left_line[1]), (left_line[2], left_line[3]), color, thickness)
    
#     if right_line is not None:
#         cv2.line(line_img, (right_line[0], right_line[1]), (right_line[2], right_line[3]), color, thickness)
    
#     # Create a filled polygon for the lane area
#     if left_line is not None and right_line is not None:
#         pts = np.array([[left_line[0], left_line[1]], 
#                        [left_line[2], left_line[3]], 
#                        [right_line[2], right_line[3]], 
#                        [right_line[0], right_line[1]]], np.int32)
#         cv2.fillPoly(line_img, [pts], (0, 255, 0, 50))
    
#     return cv2.addWeighted(img, 0.8, line_img, 0.2, 0.0)

# def detect_yellow_and_white_lanes(image):
#     """
#     Detects yellow and white lane markings using improved color filtering.
#     """
#     # Convert to HLS color space for better color segmentation
#     hls = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    
#     # Yellow lane detection (more precise thresholds)
#     lower_yellow = np.array([15, 80, 120], dtype=np.uint8)
#     upper_yellow = np.array([35, 255, 255], dtype=np.uint8)
#     yellow_mask = cv2.inRange(hls, lower_yellow, upper_yellow)
    
#     # White lane detection (improved thresholds)
#     lower_white = np.array([0, 200, 0], dtype=np.uint8)
#     upper_white = np.array([180, 255, 255], dtype=np.uint8)
#     white_mask = cv2.inRange(hls, lower_white, upper_white)
    
#     # Combine masks
#     lane_mask = cv2.bitwise_or(yellow_mask, white_mask)
    
#     # Apply morphological operations to clean up the mask
#     kernel = np.ones((3, 3), np.uint8)
#     lane_mask = cv2.morphologyEx(lane_mask, cv2.MORPH_CLOSE, kernel)
#     lane_mask = cv2.morphologyEx(lane_mask, cv2.MORPH_OPEN, kernel)
    
#     return lane_mask

# def create_roi_mask(image):
#     """
#     Creates a region of interest mask based on the highway perspective.
#     """
#     height, width = image.shape[:2]
    
#     # Define ROI vertices for highway perspective
#     # Bottom corners
#     bottom_left = (width * 0.1, height)
#     bottom_right = (width * 0.9, height)
    
#     # Top corners (wider to capture curved lanes)
#     top_left = (width * 0.35, height * 0.6)
#     top_right = (width * 0.65, height * 0.6)
    
#     roi_vertices = np.array([bottom_left, top_left, top_right, bottom_right], dtype=np.int32)
    
#     mask = np.zeros_like(image[:, :, 0])
#     cv2.fillPoly(mask, [roi_vertices], 255)
    
#     return mask

# def detect_lane_lines(edges, roi_mask):
#     """
#     Detects lane lines using Hough Transform with improved parameters.
#     """
#     # Apply ROI mask
#     masked_edges = cv2.bitwise_and(edges, roi_mask)
    
#     # Hough Line Transform with optimized parameters
#     lines = cv2.HoughLinesP(
#         masked_edges,
#         rho=1,              # Distance resolution in pixels
#         theta=np.pi/180,    # Angle resolution in radians
#         threshold=50,        # Minimum number of votes
#         minLineLength=40,   # Minimum line length
#         maxLineGap=20       # Maximum gap between line segments
#     )
    
#     return lines

# def separate_left_right_lines(lines, image_width):
#     """
#     Separates detected lines into left and right lanes based on slope.
#     """
#     left_lines = []
#     right_lines = []
    
#     if lines is not None:
#         for line in lines:
#             x1, y1, x2, y2 = line.reshape(4)
            
#             # Calculate slope
#             if x2 - x1 == 0:  # Vertical line
#                 continue
                
#             slope = (y2 - y1) / (x2 - x1)
            
#             # Filter lines based on slope and position
#             if abs(slope) < 0.5:  # Too horizontal
#                 continue
                
#             # Separate left and right lines
#             if slope < 0 and x1 < image_width/2:  # Left lane
#                 left_lines.append(line)
#             elif slope > 0 and x1 > image_width/2:  # Right lane
#                 right_lines.append(line)
    
#     return left_lines, right_lines

# def fit_polynomial_to_lines(lines, image_height):
#     """
#     Fits a polynomial to the detected lines for smooth lane representation.
#     """
#     if not lines:
#         return None
    
#     # Extract all points from lines
#     points = []
#     for line in lines:
#         x1, y1, x2, y2 = line.reshape(4)
#         points.append([x1, y1])
#         points.append([x2, y2])
    
#     points = np.array(points)
    
#     if len(points) < 2:
#         return None
    
#     # Fit polynomial (degree 1 for straight lines, degree 2 for curves)
#     try:
#         coeffs = np.polyfit(points[:, 1], points[:, 0], 1)
#         return coeffs
#     except:
#         return None

# def generate_lane_coordinates(coeffs, image_height):
#     """
#     Generates lane coordinates from polynomial coefficients.
#     """
#     if coeffs is None:
#         return None
    
#     # Generate y coordinates
#     y1 = image_height
#     y2 = int(image_height * 0.6)  # 60% up the image
    
#     # Calculate x coordinates
#     x1 = int(coeffs[0] * y1 + coeffs[1])
#     x2 = int(coeffs[0] * y2 + coeffs[1])
    
#     return [x1, y1, x2, y2]

# def process_lane_detection(image):
#     """
#     Main lane detection function with improved algorithm.
#     """
#     # 1. Detect yellow and white lane markings
#     lane_mask = detect_yellow_and_white_lanes(image)
    
#     # 2. Convert to grayscale and apply Gaussian blur
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
#     # 3. Apply lane mask to blurred image
#     masked_blurred = cv2.bitwise_and(blurred, blurred, mask=lane_mask)
    
#     # 4. Edge detection
#     edges = cv2.Canny(masked_blurred, 50, 150)
    
#     # 5. Create ROI mask
#     roi_mask = create_roi_mask(image)
    
#     # 6. Detect lane lines
#     lines = detect_lane_lines(edges, roi_mask)
    
#     # 7. Separate left and right lines
#     left_lines, right_lines = separate_left_right_lines(lines, image.shape[1])
    
#     # 8. Fit polynomials to left and right lines
#     left_coeffs = fit_polynomial_to_lines(left_lines, image.shape[0])
#     right_coeffs = fit_polynomial_to_lines(right_lines, image.shape[0])
    
#     # 9. Generate lane coordinates
#     left_line = generate_lane_coordinates(left_coeffs, image.shape[0])
#     right_line = generate_lane_coordinates(right_coeffs, image.shape[0])
    
#     # 10. Draw lane lines on the image
#     result_image = draw_lane_lines(image, left_line, right_line)
    
#     return result_image 



import cv2
import numpy as np
import matplotlib.pyplot as plt

class AdvancedLaneDetector:
    """
    An advanced lane detection class that uses perspective transforms,
    combined thresholding, and polynomial fitting to detect lanes.
    """
    def __init__(self):
        # Placeholders for fitted polynomials from the last frame
        self.left_fit = None
        self.right_fit = None
        # Smoothed polynomial coefficients
        self.left_fit_smooth = None
        self.right_fit_smooth = None
        
        # Define conversion from pixels to meters
        self.ym_per_pix = 30/720  # meters per pixel in y dimension
        self.xm_per_pix = 3.7/700 # meters per pixel in x dimension

    def _combined_thresholding(self, img):
        """
        Applies a combination of color and gradient thresholding to create a
        robust binary image of potential lane pixels.
        """
        # Convert to HLS color space and separate the S channel
        hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
        s_channel = hls[:,:,2]
        
        # Sobel x gradient
        sobelx = cv2.Sobel(s_channel, cv2.CV_64F, 1, 0)
        abs_sobelx = np.absolute(sobelx)
        scaled_sobel = np.uint8(255 * abs_sobelx / np.max(abs_sobelx))
        
        # Threshold x gradient
        sxbinary = np.zeros_like(scaled_sobel)
        sxbinary[(scaled_sobel >= 20) & (scaled_sobel <= 100)] = 1
        
        # Threshold color channel
        s_binary = np.zeros_like(s_channel)
        s_binary[(s_channel >= 170) & (s_channel <= 255)] = 1
        
        # Combine the two binary thresholds
        combined_binary = np.zeros_like(sxbinary)
        combined_binary[(s_binary == 1) | (sxbinary == 1)] = 1
        
        return combined_binary

    def _perspective_warp(self, img):
        """
        Performs a perspective warp (Bird's-Eye View) on the image.
        """
        h, w = img.shape[:2]
        
        # Define source points for the perspective transform (trapezoid)
        # These points should be adjusted for your specific camera calibration
        src = np.float32([
            (595, 450),   # Top-left
            (685, 450),   # Top-right
            (1100, h),    # Bottom-right
            (200, h)      # Bottom-left
        ])
        
        # Define destination points for the warped image (rectangle)
        dst = np.float32([
            (320, 0),     # Top-left
            (960, 0),     # Top-right
            (960, h),     # Bottom-right
            (320, h)      # Bottom-left
        ])
        
        # Compute the perspective transform matrix M and its inverse Minv
        M = cv2.getPerspectiveTransform(src, dst)
        Minv = cv2.getPerspectiveTransform(dst, src)
        
        # Warp the image
        warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)
        
        return warped, Minv

    def _find_lane_pixels_sliding_window(self, warped_img):
        """
        Finds lane pixels using a sliding window approach.
        """
        histogram = np.sum(warped_img[warped_img.shape[0]//2:,:], axis=0)
        
        midpoint = np.int64(histogram.shape[0]//2)
        leftx_base = np.argmax(histogram[:midpoint])
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint
        
        nwindows = 9
        window_height = np.int64(warped_img.shape[0]//nwindows)
        margin = 100
        minpix = 50
        
        nonzero = warped_img.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        
        leftx_current = leftx_base
        rightx_current = rightx_base
        
        left_lane_inds = []
        right_lane_inds = []
        
        for window in range(nwindows):
            win_y_low = warped_img.shape[0] - (window + 1) * window_height
            win_y_high = warped_img.shape[0] - window * window_height
            win_xleft_low = leftx_current - margin
            win_xleft_high = leftx_current + margin
            win_xright_low = rightx_current - margin
            win_xright_high = rightx_current + margin
            
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]
            
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            
            if len(good_left_inds) > minpix:
                leftx_current = np.int64(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > minpix:
                rightx_current = np.int64(np.mean(nonzerox[good_right_inds]))
                
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
        
        return left_lane_inds, right_lane_inds, nonzerox, nonzeroy

    def _fit_polynomial(self, left_lane_inds, right_lane_inds, nonzerox, nonzeroy):
        """
        Fits a 2nd order polynomial to the lane pixels.
        """
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]

        try:
            self.left_fit = np.polyfit(lefty, leftx, 2)
            self.right_fit = np.polyfit(righty, rightx, 2)
        except TypeError:
            # Avoids error if no pixels were found
            print("Failed to fit polynomial, using previous fit.")
            if self.left_fit is not None and self.right_fit is not None:
                pass # Use the previous fit
            else:
                # Handle the case where there is no previous fit
                return None, None

        # Smoothing logic
        if self.left_fit_smooth is None:
            self.left_fit_smooth = self.left_fit
            self.right_fit_smooth = self.right_fit
        else:
            alpha = 0.1 # Smoothing factor
            self.left_fit_smooth = self.left_fit_smooth * (1-alpha) + self.left_fit * alpha
            self.right_fit_smooth = self.right_fit_smooth * (1-alpha) + self.right_fit * alpha

        return self.left_fit_smooth, self.right_fit_smooth

    def _measure_curvature_and_position(self, warped_img, left_fit, right_fit):
        """
        Calculates the lane curvature and vehicle position.
        """
        ploty = np.linspace(0, warped_img.shape[0]-1, warped_img.shape[0])
        y_eval = np.max(ploty)

        # Fit new polynomials to x,y in world space
        left_fit_cr = np.polyfit(ploty * self.ym_per_pix, (left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]) * self.xm_per_pix, 2)
        right_fit_cr = np.polyfit(ploty * self.ym_per_pix, (right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]) * self.xm_per_pix, 2)
        
        # Calculate the new radius of curvature
        left_curverad = ((1 + (2*left_fit_cr[0]*y_eval*self.ym_per_pix + left_fit_cr[1])**2)**1.5) / np.absolute(2*left_fit_cr[0])
        right_curverad = ((1 + (2*right_fit_cr[0]*y_eval*self.ym_per_pix + right_fit_cr[1])**2)**1.5) / np.absolute(2*right_fit_cr[0])
        
        # Calculate vehicle position
        lane_center_px = ( (left_fit[0]*y_eval**2 + left_fit[1]*y_eval + left_fit[2]) + (right_fit[0]*y_eval**2 + right_fit[1]*y_eval + right_fit[2]) ) / 2
        car_center_px = warped_img.shape[1] / 2
        offset = (car_center_px - lane_center_px) * self.xm_per_pix
        
        return (left_curverad + right_curverad)/2, offset
        
    def _draw_on_original(self, original_img, warped_img, left_fit, right_fit, Minv, curvature, offset):
        """
        Draws the detected lane back onto the original image.
        """
        warp_zero = np.zeros_like(warped_img).astype(np.uint8)
        color_warp = np.dstack((warp_zero, warp_zero, warp_zero))
        
        h, w = original_img.shape[:2]
        ploty = np.linspace(0, h-1, h)
        
        left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
        right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]
        
        pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
        pts = np.hstack((pts_left, pts_right))
        
        # Draw the lane onto the warped blank image
        cv2.fillPoly(color_warp, np.int_([pts]), (0, 255, 0))
        
        # Warp the blank back to original image space
        new_warp = cv2.warpPerspective(color_warp, Minv, (w, h))
        
        # Combine the result with the original image
        result = cv2.addWeighted(original_img, 1, new_warp, 0.3, 0)
        
        # Add text for curvature and offset
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(result, f'Radius of Curvature: {curvature:.2f} m', (50, 50), font, 1, (255, 255, 255), 2)
        cv2.putText(result, f'Vehicle Offset: {offset:.2f} m', (50, 100), font, 1, (255, 255, 255), 2)

        return result

    def process_frame(self, frame):
        """
        The main pipeline for processing a single frame/image.
        """
        # 1. Apply combined color and gradient thresholding
        binary_img = self._combined_thresholding(frame)
        
        # 2. Apply perspective warp
        warped_binary, Minv = self._perspective_warp(binary_img)
        
        # 3. Find lane pixels and fit a polynomial
        left_inds, right_inds, nz_x, nz_y = self._find_lane_pixels_sliding_window(warped_binary)
        left_fit, right_fit = self._fit_polynomial(left_inds, right_inds, nz_x, nz_y)

        # 4. Handle cases where polynomial fit fails
        if left_fit is None or right_fit is None:
            return frame # Return original frame if lanes not detected

        # 5. Measure curvature and vehicle position
        curvature, offset = self._measure_curvature_and_position(warped_binary, left_fit, right_fit)
        
        # 6. Draw the detected lane back onto the original image
        result = self._draw_on_original(frame, warped_binary, left_fit, right_fit, Minv, curvature, offset)
        
        return result

# --- Main execution function ---
# This function will be called by the execution environment.
def process_lane_detection(input_image):
    """
    Takes an input image, processes it to find lanes, and returns the result.
    """
    # Initialize the detector
    detector = AdvancedLaneDetector()
    
    # Process the frame using the detector class
    result_image = detector.process_frame(input_image)
    
    # Return the final image with lanes drawn on it.
    # THIS MUST BE a NumPy array for the display to work.
    return result_image

# You can still have a __main__ block for local testing if needed,
# but the function above is what solves the error in the execution environment.
if __name__ == '__main__':
    try:
        # Load a test image
        image = cv2.imread('test_image.jpg')
        if image is None:
            raise FileNotFoundError("Could not read 'test_image.jpg'.")
            
        # Call the main processing function
        final_result = process_lane_detection(image)
        
        # Display the result
        cv2.imshow('Advanced Lane Detection Result', final_result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please provide a valid 'test_image.jpg' in the same directory to run this test.")