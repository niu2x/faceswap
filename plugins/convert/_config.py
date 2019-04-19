#!/usr/bin/env python3
""" Default configurations for convert """

import logging

from lib.config import FaceswapConfig
from lib.utils import _video_extensions

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

BLUR_TYPES = ["gaussian", "normalized", "none"]
BLUR_INFO = ("The type of blending to use:"
             "\n\t gaussian: Blend with Gaussian filter. Slower, but often better than Normalized"
             "\n\t normalized: Blend with Normalized box filter. Faster than Gaussian"
             "\n\t none: Don't perform blending")


class Config(FaceswapConfig):
    """ Config File for Convert """

    def set_defaults(self):
        """ Set the default values for config """
        logger.debug("Setting defaults")

        # << GLOBAL OPTIONS >> #
#        section = "global"
#        self.add_section(title=section,
#                         info="Options that apply to all models")

        # << BOX OPTIONS >> #
        section = "mask.box_blend"
        self.add_section(title=section,
                         info="Options for blending the edges of the swapped box with the "
                              "background image")
        self.add_item(
            section=section, title="type", datatype=str, choices=BLUR_TYPES, default="gaussian",
            info=BLUR_INFO)
        self.add_item(
            section=section, title="distance", datatype=float, default=11.0, rounding=1,
            min_max=(0.1, 25.0),
            info="The distance from the edges of the swap box to start blending. "
                 "\nThe distance is set as percentage of the swap box size to give the number of "
                 "pixels from the edge of the box. Eg: For a swap area of 256px and a percentage "
                 "of 4%, blending would commence 10 pixels from the edge."
                 "\nHigher percentages start the blending from closer to the center of the face, "
                 "so will reveal more of the source face.")
        self.add_item(
            section=section, title="radius", datatype=float, default=5.0, rounding=1,
            min_max=(0.1, 25.0),
            info="Radius dictates how much blending should occur, or more specifically, how far "
                 "the blending will spread away from the 'distance' parameter."
                 "\nThis figure is set as a percentage of the swap box size to give the radius in "
                 "pixels. Eg: For a swap area of 256px and a percentage of 5%, the radius would "
                 "be 13 pixels"
                 "\nNB: Higher percentage means more blending, but too high may reveal more of "
                 "the source face, or lead to hard lines at the border.")
        self.add_item(
            section=section, title="passes", datatype=int, default=1, rounding=1,
            min_max=(1, 8),
            info="The number of passes to perform. Additional passes of the blending "
                 "algorithm can improve smoothing at a time cost. This is more useful for 'box' "
                 "type blending."
                 "\nAdditional passes have exponentially less effect so it's not worth setting "
                 "this too high")

        # << MASK OPTIONS >> #
        section = "mask.mask_blend"
        self.add_section(title=section,
                         info="Options for blending the edges between the mask and the "
                              "background image")
        self.add_item(
            section=section, title="type", datatype=str, choices=BLUR_TYPES, default="normalized",
            info=BLUR_INFO)
        self.add_item(
            section=section, title="radius", datatype=float, default=3.0, rounding=1,
            min_max=(0.1, 25.0),
            info="Radius dictates how much blending should occur."
                 "\nThis figure is set as a percentage of the mask diameter to give the radius in "
                 "pixels. Eg: for a mask with diameter 200px, a percentage of 6% would give a "
                 "final radius of 3px."
                 "\nHigher percentage means more blending")
        self.add_item(
            section=section, title="passes", datatype=int, default=4, rounding=1,
            min_max=(1, 8),
            info="The number of passes to perform. Additional passes of the blending "
                 "algorithm can improve smoothing at a time cost. This is more useful for 'box' "
                 "type blending."
                 "\nAdditional passes have exponentially less effect so it's not worth setting "
                 "this too high")
        self.add_item(
            section=section, title="erosion", datatype=float, default=0.0, rounding=1,
            min_max=(-100.0, 100.0),
            info="Erosion kernel size as a percentage of the mask radius area.\n"
                 "Positive values apply erosion which reduces the size of the swapped area.\n"
                 "Negative values apply dilation which increases the swapped area")

        # << COLOR OPTIONS >> #
        section = "color.color_transfer"
        self.add_section(title=section,
                         info="Options for transfering the color distribution from the source to "
                              "the target image using the mean and standard deviations of the "
                              "L*a*b* color space.\n"
                              "This implementation is (loosely) based on to the 'Color Transfer "
                              "between Images paper by Reinhard et al., 2001. matching the "
                              "histograms between the source and destination faces.")
        self.add_item(
            section=section, title="clip", datatype=bool, default=True,
            info="Should components of L*a*b* image be scaled by np.clip before converting back "
                 "to BGR color space?\n"
                 "If False then components will be min-max scaled appropriately.\n"
                 "Clipping will keep target image brightness truer to the input.\n"
                 "Scaling will adjust image brightness to avoid washed out portions in the "
                 "resulting color transfer that can be caused by clipping.")
        self.add_item(
            section=section, title="preserve_paper", datatype=bool, default=True,
            info="Should color transfer strictly follow methodology layed out in original paper?\n"
                 "The method does not always produce aesthetically pleasing results.\n"
                 "If False then L*a*b* components will be scaled using the reciprocal of the "
                 "scaling factor proposed in the paper. This method seems to produce more "
                 "consistently aesthetically pleasing results")

        section = "color.match_hist"
        self.add_section(title=section,
                         info="Options for matching the histograms between the source and "
                              "destination faces")
        self.add_item(
            section=section, title="threshold", datatype=float, default=99.0, rounding=1,
            min_max=(90.0, 100.0),
            info="Adjust the threshold for histogram matching. Can reduce extreme colors leaking "
                 "in by filtering out colors at the extreme ends of the histogram spectrum")

        # << POST WARP OPTIONS >> #
        section = "scaling.sharpen"
        self.add_section(title=section,
                         info="Options for sharpening the face after placement")
        self.add_item(
            section=section, title="method", datatype=str,
            choices=["box", "gaussian", "unsharp_mask"], default="unsharp_mask",
            info="The type of sharpening to use: "
                 "\n\t box: Fastest, but weakest method. Uses a box filter to assess edges."
                 "\n\t gaussian: Slower, but better than box. Uses a gaussian filter to assess "
                 "edges."
                 "\n\t unsharp-mask: Slowest, but most tweakable. Uses the unsharp-mask method "
                 "to assess edges.")
        self.add_item(
            section=section, title="amount", datatype=int, default=150, rounding=1,
            min_max=(100, 500),
            info="Percentage that controls the magnitude of each overshoot "
                 "(how much darker and how much lighter the edge borders become)."
                 "\nThis can also be thought of as how much contrast is added at the edges. It "
                 "does not affect the width of the edge rims.")
        self.add_item(
            section=section, title="radius", datatype=float, default=0.3, rounding=1,
            min_max=(0.1, 5.0),
            info="Affects the size of the edges to be enhanced or how wide the edge rims become, "
                 "so a smaller radius enhances smaller-scale detail."
                 "\nRadius is set as a percentage of the final frame width and rounded to the "
                 "nearest pixel. E.g for a 1280 width frame, a 0.6 percenatage will give a radius "
                 "of 8px."
                 "\nHigher radius values can cause halos at the edges, a detectable faint light "
                 "rim around objects. Fine detail needs a smaller radius. "
                 "\nRadius and amount interact; reducing one allows more of the other.")
        self.add_item(
            section=section, title="threshold", datatype=float, default=5.0, rounding=1,
            min_max=(1.0, 10.0),
            info="[unsharp_mask only] Controls the minimal brightness change that will be "
                 "sharpened or how far apart adjacent tonal values have to be before the filter "
                 "does anything."
                 "\nThis lack of action is important to prevent smooth areas from becoming "
                 "speckled. The threshold setting can be used to sharpen more pronounced edges, "
                 "while leaving subtler edges untouched. "
                 "\nLow values should sharpen more because fewer areas are excluded. "
                 "\nHigher threshold values exclude areas of lower contrast.")

        # << VIDEO ENCODING OPTIONS >> #
        section = "video.global"
        self.add_section(title=section,
                         info="Options for encoding converted videos")
        self.add_item(
            section=section, title="container", datatype=str, default="mp4",
            choices=[ext.replace(".", "") for ext in _video_extensions],
            info="Video container to use.")
        self.add_item(
            section=section, title="codec", datatype=str,
            choices=["libx264", "libx265"], default="libx264",
            info="Video codec to use:\n"
                 "libx264: H.264. A widely supported and commonly used codec.\n"
                 "libx265: H.265 / HEVC video encoder application library.")

        section = "video.libx264"
        self.add_section(title=section,
                         info="Options for h.264 encoding")
        self.add_item(
            section=section, title="crf", datatype=int, min_max=(0, 51), rounding=1, default=23,
            info="Constant Rate Factor:  0 is lossless and 51 is worst quality possible. A lower "
                 "value generally leads to higher quality, and a subjectively sane range is "
                 "17–28. Consider 17 or 18 to be visually lossless or nearly so; it should look "
                 "the same or nearly the same as the input but it isn't technically lossless.\n"
                 "The range is exponential, so increasing the CRF value +6 results in roughly "
                 "half the bitrate / file size, while -6 leads to roughly twice the bitrate.\n"
                 "Choose the highest CRF value that still provides an acceptable quality. If the "
                 "output looks good, then try a higher value. If it looks bad, choose a lower "
                 "value.")
        self.add_item(
            section=section, title="preset", datatype=str, default="medium",
            choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow",
                     "slower", "veryslow"],
            info="A preset is a collection of options that will provide a certain encoding speed "
                 "to compression ratio. A slower preset will provide better compression "
                 "(compression is quality per filesize). Use the slowest preset that you have "
                 "patience for")
        self.add_item(
            section=section, title="tune", datatype=str, default="none",
            choices=["none", "film", "animation", "grain", "stillimage", "fastdecode",
                     "zerolatency"],
            info="Change settings based upon the specifics of your input:\n"
                 "film: use for high quality movie content; lowers deblocking.\n\t"
                 "animation: good for cartoons; uses higher deblocking and more reference "
                 "frames.\n\t"
                 "grain: preserves the grain structure in old, grainy film material.\n\t"
                 "stillimage: good for slideshow-like content.\n\t"
                 "fastdecode: allows faster decoding by disabling certain filters.\n\t"
                 "zerolatency: good for fast encoding and low-latency streaming.")
        self.add_item(
            section=section, title="profile", datatype=str, default="auto",
            choices=["auto", "baseline", "main", "high", "high10", "high422", "high444"],
            info="Limit the output to a specific H.264 profile. Don't change this unless your "
                 "target device only supports a certain profile.")
        self.add_item(
            section=section, title="level", datatype=str, default="auto",
            choices=["auto", "1", "1b", "1.1", "1.2", "1.3", "2", "2.1", "2.2", "3", "3.1", "3.2",
                     "4", "4.1", "4.2", "5", "5.1", "5.2", "6", "6.1", "6.2"],
            info="Set the encoder level, Don't change this unless your target device only "
                 "supports a certain level.")

        section = "video.libx265"
        self.add_section(title=section,
                         info="Options for h.265 / HEVC encoding")
        self.add_item(
            section=section, title="crf", datatype=int, min_max=(0, 51), rounding=1, default=28,
            info="Constant Rate Factor:  0 is lossless and 51 is worst quality possible. A lower "
                 "value generally leads to higher quality, and a subjectively sane range is "
                 "17–28. Consider 17 or 18 to be visually lossless or nearly so; it should look "
                 "the same or nearly the same as the input but it isn't technically lossless.\n"
                 "The range is exponential, so increasing the CRF value +6 results in roughly "
                 "half the bitrate / file size, while -6 leads to roughly twice the bitrate.\n"
                 "Choose the highest CRF value that still provides an acceptable quality. If the "
                 "output looks good, then try a higher value. If it looks bad, choose a lower "
                 "value.")
        self.add_item(
            section=section, title="preset", datatype=str, default="medium",
            choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow",
                     "slower", "veryslow"],
            info="A preset is a collection of options that will provide a certain encoding speed "
                 "to compression ratio. A slower preset will provide better compression "
                 "(compression is quality per filesize). Use the slowest preset that you have "
                 "patience for")
        self.add_item(
            section=section, title="tune", datatype=str, default="none",
            choices=["none", "grain", "fastdecode", "zerolatency"],
            info="Change settings based upon the specifics of your input:\n"
                 "grain: preserves the grain structure in old, grainy film material.\n\t"
                 "fastdecode: allows faster decoding by disabling certain filters.\n\t"
                 "zerolatency: good for fast encoding and low-latency streaming.")
