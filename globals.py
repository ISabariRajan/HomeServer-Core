from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as ImageImage
# from PIL.ImageTk import PhotoImage
from os import listdir
from os.path import join as joinpath, dirname
import cv2
from cv2 import imencode, cvtColor, COLOR_BGRA2BGR, COLOR_RGB2BGR
import numpy as np
from pathlib import Path
import base64
import copy as cpy
Image.MAX_IMAGE_PIXELS = 438052650

def deepcopy(obj):
  return cpy.deepcopy(obj)

def copy(obj):
  return cpy.copy(obj)

def join(*args):
  return Path(joinpath(args[0], *args[1:]))

from settings import fonts_dir, images_dir, logos_dir

class Fonts:
  century_gothic = ImageFont.truetype(join(fonts_dir, "Century Gothic.ttf"), 100)
  kugile = ImageFont.truetype(join(fonts_dir, "Kugile_Demo.ttf"), 100)

fonts = Fonts()

class Colors:
  white_full = (255, 255, 255, 255)
  transparent = (255, 255, 255, 0)

colors = Colors()

class SharedObject:
  whatsapp_logo: Image
  company_logo: Image
  original_image: Image
  updated_image: Image
  whatsapp_contact_number: str = "+91-8015399392"

class ImageOverlayConfiguration:
  image: ImageImage = None
  bbox: tuple = ()
  border_radius: int = None
  border_width: int = None
  height: int = None
  width: int = None
  size: tuple = None
  x: int = None
  y: int = None
  x1: int = None
  y1: int = None
  half_width: float = None
  half_height: float = None
  half_x: float = None
  hlaf_y: float = None
  padding: int = None
  inner_overlay_configs: list['ImageOverlayConfiguration']
  is_crop: bool = False
  is_overlay: bool = False
  is_box: bool = False
  name: str

  def __init__(self) -> None:
    self.image = None
    self.bbox = ()
    self.border_radius = None
    self.border_width = None
    self.height = None
    self.width = None
    self.size = None
    self.x = None
    self.y = None
    self.x1 = None
    self.y1 = None
    self.half_width = None
    self.half_height = None
    self.half_x = None
    self.hlaf_y = None
    self.padding = None
    self.inner_overlay_configs = []
    self.is_crop = False
    self.is_overlay = False
    self.is_box = False
    self.name = None

  def bbox_to_xy(self):
    bbox = self.bbox
    if bbox:
      self.x = bbox[0]
      self.y = bbox[1]
      self.x1 = bbox[2]
      self.y1 = bbox[3]

  def xy_bbox(self):
    self.bbox = (self.x, self.y, self.x1, self.y1)

  def default_bbox(self):
    self.bbox = (0, 0, self.width, self.height)
    self.bbox_to_xy()
    self.xy_to_dimension()

  def xy_to_dimension(self):
      self.width = self.x1 - self.x
      self.height = self.y1 - self.y
      self.half_width = self.width / 2
      self.half_height = self.height / 2
      self.half_x = (self.x + self.x1) / 2
      self.half_y = (self.y + self.y1) / 2
  
  def get_inner_bbox_by_padding(self):
    bbox = ImageOverlayConfiguration()
    bbox.bbox = (
      self.x + self.padding,
      self.y + self.padding,
      self.x1 - self.padding,
      self.y1 - self.padding
    )
    bbox.bbox_to_xy()
    bbox.xy_to_dimension()
    return bbox

  def get_inner_bbox_by_align(self, align, config: 'ImageOverlayConfiguration') -> 'ImageOverlayConfiguration':
    if ('bbox' not in config.__dict__) or (not config.bbox):
      config.default_bbox()
    width = config.width
    height = config.height
    if (not width) or (not height):
      config.xy_to_dimension()

    if align == "TL":
      config.x = self.x + self.padding
      config.y = self.y + self.padding
      config.x1 = self.x + self.padding + config.width
      config.y1 = self.y + self.padding + config.height
    if align == "TC":
      config.x = int(self.half_x - config.half_width)
      config.y = self.y + self.padding
      config.x1 = int(self.half_x + config.half_width)
      config.y1 = self.y + self.padding + config.height
    if align == "TR":
      config.x = self.x1 - self.padding - config.width
      config.y = self.y + self.padding
      config.x1 = self.x1 - self.padding
      config.y1 = self.y + self.padding + config.height

    if align == "CL":
      config.x = self.x + self.padding
      config.y = int(self.half_x - config.half_width)
      config.x1 = self.x + self.padding + config.width
      config.y1 = int(self.half_y + config.half_height)
    if align == "CC":
      config.x = int(self.half_x - config.half_width)
      config.y = int(self.half_y - config.half_height)
      config.x1 = int(self.half_x + config.half_width)
      config.y1 = int(self.half_y + config.half_height)
    if align == "CR":
      config.x = self.x1 - self.padding - config.width
      config.y = int(self.half_y - config.half_height)
      config.x1 = self.x1 - self.padding
      config.y1 = int(self.half_y + config.half_height)

    if align == "BL":
      config.x = self.x + self.padding
      config.y = self.y1 - self.padding - config.height
      config.x1 = self.x + self.padding + config.width
      config.y1 = self.y1 - self.padding
    if align == "BC":
      config.x = int(self.half_x - config.half_width)
      config.y = self.y1 - self.padding - config.height
      config.x1 = int(self.half_x + config.half_width)
      config.y1 = self.y1 - self.padding
    if align == "BR":
      config.x = self.x1 - self.padding - config.width
      config.y = self.y1 - self.padding - config.height
      config.x1 = self.x1 - self.padding
      config.y1 = self.y1 - self.padding
    
    config.xy_bbox()
    return config

class OverlayConfiguration:
  inner_border_box: ImageOverlayConfiguration
  image_size: tuple
  whatsapp_contact_width: int

overlay_configuration = OverlayConfiguration()

class Configuration:
  width: int
  height: int

class Instagram:
  square_feed: Configuration = Configuration()
  landscape: Configuration = Configuration()
  potrait_feed: Configuration = Configuration()
  story: Configuration = Configuration()
  reel: Configuration = Configuration()

instagram_config = Instagram()
instagram_config.square_feed.height = 1080
instagram_config.square_feed.width = 1080
instagram_config.landscape.height = 566
instagram_config.landscape.width = 1080
instagram_config.potrait_feed.height = 1350
instagram_config.potrait_feed.width = 1080
instagram_config.story.height = 1920
instagram_config.story.width = 1080
instagram_config.reel.height = 1920
instagram_config.reel.width = 1080


youtube_config = Configuration()
youtube_config.width = 1080
youtube_config.height = 1080

# 1 BOX 790D79 Opacity 40% 34.7727 Font Size

# 2 BOX 400542 Opacity 70% 28.4091 Font Size

# out line around 35 px


shared_obj = SharedObject()
from packages.image_process import ImageProcessor
img_processor = ImageProcessor()

from packages.generic_image_process import GenericImageProcess
gen_img_processor = GenericImageProcess()