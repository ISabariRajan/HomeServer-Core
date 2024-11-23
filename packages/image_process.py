from globals import join, listdir
from globals import colors
from globals import Image, ImageDraw, ImageFont, ImageImage
from globals import imencode, cvtColor
from globals import np, base64
from globals import COLOR_RGB2BGR

transparent_color = colors.transparent

class OSOperation:
  def list_images_in_folder(self, input_folder):
    valid_images = []
    for curr_file in listdir(input_folder):
      if curr_file.lower().endswith((".jpeg", ".jpg", ".png")):
          valid_images.append(curr_file)
    return valid_images

class ImageOperation:
  def get_avg_image_size(self, folder_name, image_list):
    total_width = 0
    total_height = 0
    total_images = 0
    for curr_file in image_list:
      curr_file = join(folder_name, curr_file)
      image = Image.open(curr_file)
      w, h = image.size
      total_height += h
      total_width += w
      total_images += 1

    avg_width = int(total_width/total_images)
    avg_height = int(total_height/total_images)
    return avg_width, avg_height

class ImageProcessor:
  def open_rgba_image(self, image_path) -> Image:
    return Image.open(image_path).convert("RGBA")

  def new_layer(self, fill_color=transparent_color):
    return Image.new("RGBA", (2000, 2000), fill_color)

  def to_rgba(self, img):
    if img.mode != "RGBA":
      return img.convert("RGBA")
    return img

  def to_rgb(self, img):
    if img.mode != "RGB":
      return img.convert("RGB")
    return img

  def draw_rectange_over_image(
        self,
        image,
        rect_axis = [10, 10, 110, 120],
        fill_color = (0, 0, 255, 0),
        outline_color = (0, 0, 255),
        border_width = 2,
        border_radius = 300,
        is_png = True
      ):
    rect_img = Image.new(image.mode, image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(rect_img)
    if border_radius:
      draw.rounded_rectangle(
        rect_axis,
        fill=fill_color,
        outline=outline_color,
        width=border_width,
        radius=border_radius
      )
    else:
      draw.rectangle(
        rect_axis,
        fill=fill_color,
        outline=outline_color,
        width=border_width
      )
    return Image.alpha_composite(image, rect_img)

  def create_text_image(
    self,
    text,
    font,
    fill_color=(0, 0, 255)
  ):
    img = Image.new("RGBA", (2000,2000), transparent_color)
    draw_obj = ImageDraw.Draw(img)
    # font = ImageFont.truetype(font_config["name"], size=font_config["size"])
    draw_obj.text((0, 0), text=text, font=font, fill=fill_color)
    bbox = font.getbbox(text)
    img = img.crop(bbox)
    return img
  
  def add_fill_background(self, img, fill_color):
    layer = self.new_layer(fill_color)
    crop_val = img.getbbox()
    new_img = self.draw_overlay(
      img, layer, (0, 0)
    )
    return new_img.crop(crop_val)
  
  def draw_overlay(
    self,
    bg_image,
    fg_image,
    fg_image_axis,
    fg_image_resize=None,
    fg_image_preserve_ar=True
  ):
    fg_img = self.to_rgba(fg_image)
    bg_img = self.to_rgba(bg_image)
    print(fg_img.size, bg_img.size)
    # return fg_img
    if fg_image_resize:
      fg_img = self.resize_image(fg_img, fg_image_resize, fg_image_preserve_ar)
    new_image = Image.new("RGBA", bg_img.size)
    new_image.paste(fg_img, fg_image_axis, fg_img)
    bg_img.paste(new_image, (0,0), mask=new_image)
    return Image.alpha_composite(bg_img, new_image)
  
  def resize_image_by_width(
      self,
      img,
      resize_width
  ) -> ImageImage:

    scale_factor = resize_width/img.width
    img_re_size = (int(img.width * scale_factor), int(img.height * scale_factor))
    return self.resize_image(img, img_re_size, preserve_aspect_ratio=True)
  
  def draw_text_to_image(
      self,
      img,
      text,
      font_config,
      axis,
      fill_color = (255,0,0),
      text_width=None
    ):
    text_img = self.create_text_image(text, font_config, fill_color)
    if text_width:
      scale_factor = text_width/text_img.width
      text_img_resize = (int(text_img.width * scale_factor), int(text_img.height * scale_factor))
    else:
      text_img_resize = None

    return self.draw_overlay(img, text_img,axis, fg_image_resize=text_img_resize)

  def PIL_to_CV2(self, img, format=".png"):
    np_array = cvtColor(np.array(img), COLOR_RGB2BGR)
    return imencode(".png", np_array)
  
  def PIL_to_CV2_bytes(self, img, format=".png"):
    cv2_image = self.PIL_to_CV2(img, format)
    return cv2_image[1].tobytes()

  def encode_image(self, img, is_string=True):
    base64_bytes = base64.b64encode(img)
    return str(base64_bytes, "ascii")

  def resize_image(self, img: ImageImage, new_size, preserve_aspect_ratio=False) -> ImageImage:
    if(preserve_aspect_ratio):
      width, height = img.size
      w1, h1 = new_size
      scale_factor = min(w1/width, h1,height)
      return img.resize((int(scale_factor * width), int(scale_factor * height)), Image.Resampling.LANCZOS)
    return img.resize(new_size)