from fastapi import APIRouter, Request, Response
from globals import img_processor, images_dir
from globals import shared_obj
from globals import gen_img_processor
from globals import images_dir, logos_dir
from globals import join, deepcopy
router = APIRouter()

@router.get("/")
async def index(request: Request, response: Response):
  return {"Hello": "World"}

@router.get("/init")
async def init_all(request: Request, response: Response):
  image_path = join(images_dir, "saree.jpeg")
  shared_obj.original_image = img_processor.open_rgba_image(image_path)

  image_path = join(images_dir, "thaya-thread-hi-res-logo.png")
  img = img_processor.open_rgba_image(image_path)
  img = img_processor.resize_image_by_width(img, 600)
  shared_obj.company_logo = img
  return {"Hello": "World"}

@router.get("/new")
async def new_image(request: Request, response: Response):
  img = img_processor.new_layer()
  cv2_image = img_processor.PIL_to_CV2_bytes(img)
  return Response(content=cv2_image, media_type="image/png")

@router.get("/original")
async def get_original_image(request: Request, response: Response):
  cv2_image = img_processor.PIL_to_CV2_bytes(shared_obj.original_image)
  return Response(content=cv2_image, media_type="image/png")

@router.get("/updated")
async def get_updated_image(request: Request, response: Response):
  original_image = deepcopy(shared_obj.original_image)
  print(original_image.size)
  shared_obj.updated_image = gen_img_processor.process_image(original_image, "AAA-000000")
  cv2_image = img_processor.PIL_to_CV2_bytes(shared_obj.updated_image)
  return Response(content=cv2_image, media_type="image/png")
