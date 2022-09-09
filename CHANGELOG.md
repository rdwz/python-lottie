## Unreleased (0.7.0)
 * Improved color management
 * More accurate path shape bounding box
 * More intuitive function to import lottie
 * Utility to export to a neural network
 * Fixed SVG gradients import with default attributes
 * Added support for text stroke
 * Chart drawing library
 * Renamed `utils.ellipse.Ellipse.to_bezier()` to `.to_bezier_points()`
 * Updated object model:
    * The base class `Layer` has been split into `Layer` and `VisualLayer`
    * `Layer.stretch` has been renamed to `Layer.time_stretch`
    * Added layer styles
    * `Image` asset has been split into `FileAsset` and `Image`
    * `Image.image` has been renamed to `Image.file_name`
    * `Image.image_path` has been renamed to `Image.path`
    * `Image.image_data()` has been renamed to `Image.data()`
    * Added sound asset / layer
    * Added data source asset / layer
    * Added camera layer
    * Added a lot of missing properties throughout
    * `TextDocument.color` renamed to `TextDocument.fill_color`

## 0.6.11 - 2022-01-20
 * Fancy text formatting renderer
 * Added PuckerBloat support
 * Fixed SVG conversion when the transform is missing
 * Lottie from textual description
 * Improved ellipse arc to cubic bezier conversion
 * Fixed splitting beziers with less than 2 points
 * Added more lottie objects to the model
 * Customizable export width/height
 * Improved pixel art conversion
 * More options for tracing bitmaps

## 0.6.10 - 2021-09-18
 * Glaxnimate compatibility

## 0.6.9 - 2021-08-10
 * Fixed SVG viewBox parsing
 * Fixed GIF/WebP rendering
 * Fixed vectorization issues
 * Emoji SVG filenames can be upper case
 * Fixed loading SVG polyline

## 0.6.8 - 2021-08-02
 * Fixed font fallback
 * Optional glaxnimate integration
 * Animated SVG output
 * Improved Emoji detection
 * Improved vectorization

## 0.6.7 - 2021-03-23
 * Improved text layer support
 * Fixed effect parsing

## 0.6.6 - 2020-10-07
 * Synfig importer improvements
 * SVG exporter improvements
 * GIF exporter made to render every frame by default
 * Moved project to a group on gitlab

## 0.6.5 - 2020-07-10
 * Text rendering improvements
 * SVG importer improvements
 * SVG exporter improvements
 * GIF exporter improvements
 * Fixed blender addon packaging issues

## 0.6.4 - 2020-06-16
 * Lottie parser improvements
 * Synfig importer improvements
 * SVG exporter improvements
 * Blender addon improvements
 * New script to show missing optional dependencies
 * Speed change on conversion
 * WebP exporter improvements

## 0.6.3 - 2020-05-09
 * SVG exporter improvements
 * SVG importer improvements
 * Implemented Alpha/Luma mattes on SVG export
 * Find/replace in lottie gui code editor
 * Properly parse transforms with xplit x/y
 * Krita importer

## 0.6.2 - 2020-04-30
 * Support for all importers / exporters in lottie GUI
 * JSON / Source editing in lottie GUI
 * SVG importer improvements
 * Python console in lottie GUI
 * SVG exporter improvements
 * Used a more convenient class for color values

## 0.6.1 - 2020-04-25
 * Made scripts more user friendly
 * SVG importer improvements
 * Fixed bounding box calculations on rotated groups
 * Importers for raster images without vectorization
 * SVG exporter improvements
 * Experimental GUI viewer

## 0.6.0 - 2020-04-22
 * Made scripts prefer the correct library version when running from source
 * Renamed the project to Lottie
 * Renamed most of the code that referenced Tgs

## 0.5.4 - 2020-04-22
 * Implemented rendering of smooth spatial keyframes
 * Implemented rendering of auto-orient layers
 * Automatically embed images from dotLottie archives
 * SVG exporter improvements
 * Automatic image packaging in dotLottie exporter
 * Improved api for managing layer parenting
 * Fixed lottie parsing regression

## 0.5.3 - 2020-04-21
 * Improved input options for tgsconvert
 * SVG exporter improvements
 * Fixed some packaging issue

## 0.5.2 - 2020-04-20
 * SVG exporter improvements
 * SVG importer improvements
 * Synfig importer improvements
 * Implemented fill rule
 * Partial support for text layers on SVG export
 * Support solid color layers on SVG export
 * Partial support for trim paths on SVG export
 * Added support for dotLottie
 * Fixed raster animation output of trimmed paths

## 0.5.1 - 2020-04-19
 * Added support for precomposition on SVG exporter
 * SVG exporter improvements
 * Added TIFF importer/exporter
 * Implemented Masks on SVG export
 * Added WebP importer
 * Improved loading frames from raster files
 * Added support for image layers on SVG exporter

## 0.5.0 - 2020-04-18
 * Animated WebP support
 * Support for the new Synfig plugin system
 * SVG importer improvements
 * Text rendering improvements
 * Compressed SVG import/export support
 * Sif importer improvements
 * Transformation matrix support
 * Added support for precompositions
 * Added support for shashed strokes
 * Extended FontShape to support font filenames
 * Experimental javascript binding for lottie manipulation functionality
 * Lottie parsing improvements
 * Support for transparent gradients
 * Support for Postscript type 1 fonts
 * Added easing support on shake animation utility
 * Emoji to SVG support in the text renderer
 * More user friendly gradient manipulation
 * Refactored font rendering and fallback classes

## 0.4.4 - 2020-03-31
 * Bug fixes

## 0.4.3 - 2020-03-31
 * Bug fixes

## 0.4.2 - 2020-03-31
 * Synfig importer improvements
 * SVG importer improvements
 * Refactored importers code
 * Color comparison script

## 0.4.1 - 2020-03-26
 * Documentation / packaging fixes

## 0.4.0 - 2020-03-26
 * Extended Telegram sticker validation
 * Synfig importer
 * New Synfig exporter
 * Fixed some lottie effects

## 0.3.6 - 2020-01-19
 * Support for exporting layers as frames in Inkscape
 * Improved grouping on shapes from the text renderer
 * SVG importer improvements
 * GIF exporter improvements
 * Telegram sticker restriction validation
 * Added easing support on 3D Rotation utility
 * Improved keyframe interpolation

## 0.3.5 - 2019-10-27
 * SVG exporter improvements
 * Text rendering improvements
 * Improved lottie diff script
 * SVG groups as animation layers on import

## 0.3.4 - 2019-09-09
 * SVG exporter improvements
 * Improved shape bounding box evaluation
 * Lottie object visitor functionality
 * GIF exporter improvements
 * Synfig exporter improvements
 * Pixel art vectorization
 * Lottie optimizer to reduce file size
 * Improved follow path animation utility
 * Color space management functionality

## 0.3.3 - 2019-08-12
 * Support for SMIL animations in SVG importer
 * Blender addon: Bezier improvements
 * Blender addon: Grease pencil support

## 0.3.2 - 2019-08-06
 * Blender addon

## 0.3.1 - 2019-08-04
 * SVG exporter improvements
 * Telegram sticker sanitizer
 * Text renderer fallback font
 * Using the text renderer on imported SVG
 * System to define custom lottie objects

## 0.3.0 - 2019-08-01
 * Added support for more layer effects
 * SVG parsing improvements
 * SVG exporter improvements
 * Added support for solid color layers
 * Added support for text layers
 * Inkscape extension
 * Refactored easing functions
 * Synfig exporter improvements
 * PNG exporter
 * GIF exporter
 * Video exporter
 * Text to bezier rendering

## 0.2.0 - 2019-07-26
 * Added support for Lottie shape modifiers
 * Added support for layer masks
 * Added support for layer effects
 * Added support for image layers
 * Added support for matte layers
 * Refactored Lottie shapes

## 0.1.1 - 2019-07-24
 * SVG parsing improvements
 * SVG exporter
 * Animation utilities
     * Shaking
     * Bounce
     * Follow bezier
     * Bezier in/out
     * Wave
     * 3D Rotation
     * Customizable displacer
 * Example scripts
 * Refactored Lottie animatable values
 * Automed documentation of Lottie classes
 * CSS color to lottie script
 * Vectorization using Potrace
 * Synfig exporter
 * Animation interpolation / easing
 * Bezier editing functionality
 * IK solver
 * Using vectors for Lottie values
 * TGS optimization functionality
 * Lottie HTML export
 * Unified conversion script
 * Functionality to find shapes in a group
 * Shape bounding box evaluation

## 0.1.0 - 2019-07-10
 * Basic Lottie Support
 * TGS <-> Lottie conversion
 * Lottie Diff script
 * Lottie inspection script
 * SVG importer
 * Vector algebra support
