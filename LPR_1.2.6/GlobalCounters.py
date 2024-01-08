#module variables ############################

conf,text = [],[]
text_conf,text_text = [],[]
previe_posList= []
result_text,result_conf= [],[]
result_char = []
result_char_conf = []
carCondition = 0
startCar = 0
startCarNext = 0
carSituation =0
prevgray = None
currgray = None
Temp_StartFrame = None

refPt = []
refPt_moving = []
movingPos = []
cropping = False 
GlobalRoi = None
GlobalImage = None
GlobalImage_Ori = None


##############################
tasseract_8char_conf = []
tasseract_8char_text = []
tasseract_7number_conf = []
tasseract_7number_text = []
tasseract_1char_conf = []
tasseract_1char_text = []

green_f_text =[]
green_f_conf =[]
green_f_number_text =[]
green_f_number_conf =[]

green_s_number_text =[]
green_s_number_conf =[]

green_number_text = []
green_number_conf = []
#####

carCount =None
minIndex = []
######
mysocket=None

HOST = "210.119.32.94"
PORT = 4000

Moving_Sensitive = 0.51
Stop_Sensitive = 0.1