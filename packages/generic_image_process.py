from globals import img_processor as processor, shared_obj
from globals import join, deepcopy
from globals import fonts, colors
from settings import logos_dir
from globals import OverlayConfiguration, ImageOverlayConfiguration

class GenericImageProcess:

  def __init__(self) -> None:
    logo_path = join(logos_dir, "whatsapp-logo.png")
    shared_obj.whatsapp_logo = processor.open_rgba_image(logo_path)
    shared_obj.company_logo = processor.open_rgba_image(logo_path)
    self.shared_obj = shared_obj


  def add_logo_to_image(self, img):
    # return img
    logo_img = deepcopy(self.shared_obj.company_logo)
    logo_img = processor.resize_image_by_width(logo_img, 600)
    new_logo_img = processor.add_fill_background(logo_img, (255, 255, 255, 0))
    logo_axis = (
      (int (img.width/2) - int(logo_img.width/2)),
      (int (img.height/2) - int(logo_img.height/2))
    )
    return processor.draw_overlay(
      img,
      new_logo_img,
      logo_axis
    )
  
  def add_whatsapp_contact_to_image(
        self,
        img,
        whatsapp_contact_number,
        resize_width = 400
      ):
    whatsapp_image = self.create_whatsapp_contact_image(whatsapp_contact_number)
    whatsapp_image = processor.resize_image_by_width(whatsapp_image, resize_width)
    whatsapp_image_axis = (
        (img.width - 30 - whatsapp_image.width),
        30
      )
    return processor.draw_overlay(
      img,
      whatsapp_image,
      whatsapp_image_axis
    )
  
  def add_series_to_image(self, img, series_number):
    series_image = self.create_series_image(series_number)
    series_image_axis = (
        int((img.width - series_image.width)/2),
        int(img.height - 30 - series_image.height)
      )
    return processor.draw_overlay(
      img,
      series_image,
      series_image_axis
    )

  def create_whatsapp_contact_image(self, contact_number):
    whatsapp_image = deepcopy(self.shared_obj.whatsapp_logo)
    bg_image = processor.new_layer((0,0,0,0))
    bg_image = processor.draw_overlay(bg_image, whatsapp_image, (0, 0), (100, 100))
    phone_number = processor.create_text_image(contact_number, fonts.century_gothic)
    phone_number = processor.resize_image_by_width(phone_number, 500)
    total_width = phone_number.width + 100
    bg_image = processor.draw_overlay(bg_image, phone_number, (100, 30))
    # bg_image.save("output.png")
    return bg_image.crop((0, 0, total_width, 100))
  
  def create_series_image(self, series_number):
    series_image = processor.create_text_image(series_number, fonts.century_gothic)
    # series_image.height
    series_image = processor.resize_image_by_width(series_image, 500)
    bg_image = processor.new_layer((0, 0, 0, 100))
    bg_image = processor.draw_overlay(bg_image, series_image, (0, 0))
    return bg_image.crop((0, 0, 500, series_image.height))
  
  def generate_static_template_config(self, image, padding=20):
    config = OverlayConfiguration()
    width, height = (image.size)
    config.image_size = image.size

    image_box = ImageOverlayConfiguration()
    image_box.bbox = (0, 0, width, height)
    image_box.bbox_to_xy()
    image_box.xy_to_dimension()
    image_box.padding = padding
    image_box.is_crop = True
    image_box.image = image
    image_box.name = "BG"

    inner_border_box = image_box.get_inner_bbox_by_padding()
    inner_border_box.padding = padding
    inner_border_box.border_width = int(width*0.007)
    inner_border_box.border_radius = 75
    inner_border_box.is_box = True
    inner_border_box.name = "Border"

    whatsapp = ImageOverlayConfiguration()
    whatsapp.width = int(width*0.3)
    whatsapp.is_overlay = True
    whatsapp_image = self.create_whatsapp_contact_image(shared_obj.whatsapp_contact_number)
    whatsapp_image = processor.resize_image_by_width(whatsapp_image, whatsapp.width)
    whatsapp.height = whatsapp_image.height
    whatsapp = inner_border_box.get_inner_bbox_by_align("TR", whatsapp)
    whatsapp.image = whatsapp_image
    whatsapp.name = "Whatsapp"

    logo = ImageOverlayConfiguration()
    logo.width = 600
    logo.is_overlay = True
    logo_image = deepcopy(shared_obj.company_logo)
    logo_image = processor.resize_image_by_width(logo_image, logo.width)
    logo.height = logo_image.height
    logo = inner_border_box.get_inner_bbox_by_align("BC", logo)
    logo.image = logo_image
    logo.name = "LOGO"

    image_box.inner_overlay_configs = []
    image_box.inner_overlay_configs.append(inner_border_box)
    image_box.inner_overlay_configs.append(whatsapp)
    image_box.inner_overlay_configs.append(logo)

    return image_box

  def generate_static_image(self, static_template: ImageOverlayConfiguration):
    print(f"{static_template.name}: {static_template.__dict__} {static_template.inner_overlay_configs}")
    
    bg_image = static_template.image
    if not bg_image:
      bg_image = processor.new_layer()
    if static_template.is_crop:
      bg_image = bg_image.crop(static_template.bbox)
    # return bg_image


    for template in static_template.inner_overlay_configs:
      fg_image = self.generate_static_image(template)
      if template.is_overlay:
        bg_image = processor.draw_overlay(bg_image, fg_image, template.bbox)
      if template.is_box:
        bg_image = processor.draw_rectange_over_image(
            bg_image,
            template.bbox,
            border_radius=template.border_radius,
            border_width=template.border_width
          )
    return bg_image

  def process_image(self, img, series_number):
    static_template = self.generate_static_template_config(img)
    updated_image = img
    # print(static_template.__dict__)
    # for template in static_template.inner_overlay_configs:
    #   print(template.inner_overlay_configs)
    updated_image = self.generate_static_image(static_template)
    return updated_image
    updated_image = self.add_logo_to_image(img)
    updated_image = self.add_whatsapp_contact_to_image(
        updated_image,
        shared_obj.whatsapp_contact_number,
        whatsapp_width
      )
    padding = 20
    # self.get_padded_box_of_image(updated_image)
    updated_image = processor.draw_rectange_over_image(
      image=updated_image,
      border_radius=75,
      rect_axis=box,
      border_width=border_width,
      outline_color=colors.white_full
    )
    return updated_image
    return self.add_series_to_image(updated_image, series_number)