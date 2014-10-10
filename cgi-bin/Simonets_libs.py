__author__ = 'v-user'

PATHROW_SEASON = {
    '165_67':'3-10',
    '165_68':'3-10',
    '166_63':'5-10',
    '166_64':'5-10',
    '166_65':'4-10',
    '166_66':'3-10',
    '166_67':'3-10',
    '166_68':'3-10',
    '167_63':'3-10',
    '167_64':'4-10',
    '167_65':'4-10',
    '167_66':'4-10',
    '167_67':'4-10',
    '167_68':'4-10',
    '168_61':'4-10',
    '168_62':'3-10',
    '168_63':'3-10',
    '168_64':'3-10',
    '168_65':'2-10',
    '168_66':'2-11',
    '168_67':'4-11',
    '168_68':'4-11',
    '169_61':'4-10',
    '169_62':'3-10',
    '169_63':'3-10',
    '169_64':'2-10',
    '169_65':'2-9',
    '169_66':'2-10',
    '170_61':'4-9',
    '170_62':'3-9',
    '170_63':'3-10',
    '170_64':'2-9',
    '170_65':'2-9',
    '170_66':'2-9',
    '171_61':'4-9',
    '171_62':'3-9',
    '171_63':'4-8',
    '171_64':'1-9',
    '171_65':'1-9',
    '171_66':'2-9',
    '172_61':'4-9',
    '172_62':'3-8',
    '172_63':'1-8',
    '172_64':'1-8'

}


def get_start_end_season_from_path_row(PATH_ROW):
    YY = 2014
    print PATH_ROW
    if PATHROW_SEASON.has_key(PATH_ROW):
        tmp = PATHROW_SEASON[PATH_ROW].split("-")
        # add conditions when crossing YY   now is 2013 / 2014
        return [ [2014, int(tmp[0]), 1], [2014, int(tmp[1]), 1]]
    else :
        print "No season found: using 2014 1 1 -> 2014 12 1"
        return [ [2014, 1, 1], [2014, 12, 1] ]






def rgb(r, g, b):
    return  '%02x%02x%02x' % (r, g, b)


def downLoadImage(url, out_file):

    remote_file = urllib2.urlopen(url).read()
    with open(out_file, 'wb') as file:

        file.write(remote_file)

    return

PBS_palette = '141414,ffffff,afeeee,00ffff,0000cd,0000cd,c8bedc,6495ed,0000cd,96fac8,0a6c00,008000,228b22,32cd32,beff5a,1efa1e,78a032,FF0000,FF0000,FF0000,a0e196,d2fab4,d7ee9e,FF0000,FF0000,80761a,8c961e,99c1c1,d8eea0,edffc1,f0fadc,e3e1aa,d4bdb8,ffff00,ffe1ff,8c05c6,9e847b,FF0000,FF0000,FF0000,284614,91000a,646464,8B4513'

# PBS_palette = [
#       rgb(20, 20, 20),  # 0  no data
#       rgb(255, 255, 255),  # 1  Clouds
#       rgb(175, 238, 238),  # 2  Temporary snow
#       rgb(0, 255, 255),  # 3  Snow
#       rgb(0, 0, 205),  #4   WATER  used in single date -----
#       rgb(0, 0, 205),  #5   WATER  used in single date -----
#       rgb(200, 190, 220),  # 6  Water + DRY
#       rgb(100, 149, 237) ,  #7  Water -----
#       rgb(0, 0, 205),  # 8  Water
#       rgb(150, 250, 200),  #9  WATER+FOREST -----
#       rgb(10, 108, 0) ,  #10  EVG DENSE -----
#       rgb(0, 128, 0) ,  #11  EVG DENSE -----
#       rgb(34, 139, 34) ,  #12  EVG DENSE -----
#       rgb(50, 205, 50),  #13  EVG DENSE/SHRUB -----
#       rgb(190, 255, 90) ,  #14  EVG GRASS -----
#       rgb(30, 250, 30),  # 15  EVG OPEN
#       rgb(120, 160, 50)  ,  #16  EVG SHRUB -----
#        'FF0000',  #17  EMPTY -----
#        'FF0000',  #18  EMPTY -----
#         'FF0000',  #19  EMPTY -----
#       rgb(160, 225, 150),  #20  DEC Close Humid -----
#       rgb(210, 250, 180) ,  #21  DEC Open Humid -----
#       rgb(215, 238, 158),  #22  EMPTY -----
#         'FF0000',  #23  EMPTY -----
#         'FF0000',  #24  EMPTY -----
#       rgb(128, 118, 26),  #25  DEC Close dry -----
#       rgb(140, 150, 30) ,  #26  DEC Open dry -----
#       rgb(153, 193, 193),  #27  IRRIG AGRI -----
#       rgb(216, 238, 160) ,  # 28  DEC SHRUB dense humid
#       rgb(237, 255, 193) ,  #29  DEC SHRUB  -----
#       rgb(240, 250, 220),  # 30  DEC SHRUB sparse
#       rgb(227, 225, 170) ,  #31  GRASS + bush -----
#       rgb(212, 189, 184),  #32  GRASS -----
#       rgb(255, 255, 0),  #33  EMPTY -----
#       rgb(255, 225, 255),  #34  SOIL+GRASS -----
#       rgb(140, 5, 198),  #35  SOIL -----
#       rgb(158, 132, 123),  #36  DARK SOIL -----
#         'FF0000',  #37  EMPTY -----
#         'FF0000',  #38  EMPTY -----
#         'FF0000',  #39  EMPTY -----
#       rgb(40, 70, 20),  # 40  Shawodw on vegetation
#       rgb(145, 0, 10),  # 41  Dark soil
#       rgb(100, 100, 100),  # 42  Shawodw mainly on soil
#       '8B4513',  #43  test soil -----
#   ]



CLASSvis = {
  'bands':'Class',
  'min': 0,
  'max': 43,
  'palette':PBS_palette
}


# ########################################################################################################################
# ########################################################################################################################
# # @name = PINO
# # @desc = Single date classification of TOA reflectance LANDSAT data
# # @param = image [ee.image]
# # @param = BANDS [array of bands identifier ]
# # @returns = labelled image with 1 band named 'Class' [ee.image]
# # @calling_sequence =
# # @details =
#
class PINO:

   def __init__(self, BANDS):
        self.BANDS = BANDS

   def __call__(self, image):

    BANDS = self.BANDS
    th_NDVI_MAX_WATER = 0
    BLU = image.select(BANDS[0])
    GREEN = image.select(BANDS[1])
    RED = image.select(BANDS[2])
    NIR = image.select(BANDS[3])
    SWIR1 = image.select(BANDS[4])
    SWIR2 = image.select(BANDS[5])

    # OUT=ee.Image(0)

    th_NDVI_SATURATION = 0.0037
    th_NDVI_MIN_CLOUD_BARE = 0.35
    th_NDVI_MIN_VEGE = 0.45
    th_SHALLOW_WATER = -0.1
    th_RANGELAND = 0.50
    th_GRASS = 0.55
    th_SHRUB = 0.65
    th_TREES = 0.78



    min123 = BLU.min(GREEN).min(RED)

    min1234 = min123.min(NIR)
    min234 = GREEN.min(RED).min(NIR)

    max234 = GREEN.max(RED).max(NIR)
    max1234 = max234.max(BLU)

    max57 = SWIR1.max(SWIR2)
    max457 = max57.max(NIR)

    max123457 = max1234.max(max57)


    BLUgtGREEN = BLU.gt(GREEN)
    BLUgteGREEN = BLU.gte(GREEN)
    BLUlteNIR = BLU.lte(NIR)

    GREENgtRED = GREEN.gt(RED)
    GREENlteRED = GREEN.lte(RED)
    GREENgteRED = GREEN.gte(RED)
    REDlteNIR = RED.lte(NIR)

    REDsubtractGREEN = (RED.subtract(GREEN)).abs()
    BLUsubtractNIR = BLU.subtract(NIR)

    growing14 = (BLU.lte(GREEN)).And(GREENlteRED).And(REDlteNIR)
    growing15 = growing14.And(NIR.lte(SWIR1))

    decreasing2345 = (GREENgteRED).And(RED.gte(NIR)).And(NIR.gte(SWIR1))


    SATURATION = (max234.subtract(min234)).divide(max234)

    WETNESS = image.expression('byte(b("' + BANDS[0] + '")*255)*0.2626 + byte(b("' + BANDS[1] + '")*255)*0.21 + byte(b("' + BANDS[2] + '")*255)*0.0926 + byte(b("' + BANDS[3] + '")*255)*0.0656 - byte(b("' + BANDS[4] + '")*255)*0.7629 - byte(b("' + BANDS[5] + '")*255)*0.5388')

    NDVI = (NIR.subtract(RED)).divide(NIR.add(RED))
    NDSI = (BLU.subtract(SWIR1)).divide(GREEN.add(SWIR1))

    BRIGTSOIL = ((BLU.lt(0.27)).And(growing15)).Or((BLU.lt(0.27)).And(growing14).And(((NIR.subtract(SWIR1)).gt(0.038))))

    WATERSHAPE = ((BLU.subtract(GREEN)).gt(-0.2)).And(decreasing2345).And(WETNESS.gt(0))  # add other cond
    OTHERWATERSHAPE = (BLUgteGREEN).And(GREENgteRED).And(NIR.gte(RED)).And(SWIR1.lt(NIR)).And(SWIR2.lte(SWIR1)).And(NIR.lt((RED).multiply(1.3)).And(NIR.lt(0.12)).And(SWIR1.lt(RED)).And(NIR.lte(GREEN)).And(NIR.gt(0.039)).And(WETNESS.gt(0)))  # add other cond  07/10 (add replaced with and  :) and(NIR.lte(GREEN))

    SNOWSHAPE = (min1234.gt(0.30)).And(NDSI.gt(0.65))

    CORECLOUDSHAPE = (max123457.gt(0.47)).And(min1234.gt(0.37)).And(SNOWSHAPE.eq(0)).And(BRIGTSOIL.eq(0))
    CORECLOUDSHAPE1 = ((min123.gt(0.21)).And((SWIR1).gt(min123)).And(SATURATION.gte(0.2)).And(SATURATION.lte(0.4)).And(max234.gte(0.35)).And(SNOWSHAPE.eq(0)).And(NDSI.gt(-0.3)).And(BRIGTSOIL.eq(0)).And(CORECLOUDSHAPE.eq(0)))
    CLOUDSHAPE = ((min123.gt(0.17)).And((SWIR1).gt(min123)).And(NDSI.lt(0.65)).And(max1234.gt(0.30)).And((NIR.divide(RED)).gte(1.3)).And((NIR.divide(GREEN)).gte(1.3)).And((NIR.divide(SWIR1)).gte(0.95)).And(BRIGTSOIL.eq(0)).And(CORECLOUDSHAPE.eq(0)).And(CORECLOUDSHAPE1.eq(0)))


    # main groups based on ndvi
    ndvi_1 = NDVI.lte(th_NDVI_MAX_WATER)
    ndvi_2 = NDVI.lt(th_NDVI_MIN_VEGE).And(ndvi_1.eq(0))
    ndvi_3 = NDVI.gte(th_NDVI_MIN_VEGE)


    #-------------------------------------------------------------------------------------------------------------
    #----------------------  SECTION 1 : WATER  ---------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------

    OUT = (ndvi_1.And(SNOWSHAPE)).multiply(3)
    OUT = OUT.where(((OUT.eq(0)).And(ndvi_1).And(WATERSHAPE).And(BLU.gt(0.078)).And(GREEN.gt(0.04)).And(GREEN.lte(0.12)).And(max57.lt(0.04))), 5)
    OUT = OUT.where(((OUT.eq(0)).And(ndvi_1).And(RED.gte(max457)).And(RED.lte(0.19)).And(RED.gt(0.04)).And(BLU.gt(0.078)).And(max57.lt(0.04))), 6)

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_1).And(BLU.gt(0.94)).And(GREEN.gt(0.94)).And(RED.gt(0.94)).And(NIR.gt(0.94))), 1)  # TEST CLOUDS L8


    OUT = OUT.where(((OUT.eq(0)).And(ndvi_1).And(WETNESS.gt(5))), 8)

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_1)), 7)



    #-------------------------------------------------------------------------------------------------------------
    #---------------------  SECTION 2 : CLOUDS or SOIL  ---------------------------------------------------------
    #------------------------------------------------------------------------------------------------------------

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(SNOWSHAPE)), 3)
    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(BLU.gt(0.94)).And(GREEN.gt(0.94)).And(RED.gt(0.94)).And(NIR.gt(0.94))), 1)  # TEST CLOUDS L8

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(OTHERWATERSHAPE).And(BLU.gt(0.078)).And(max57.lt(0.058))), 7)

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(CLOUDSHAPE)), 1)
    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(CORECLOUDSHAPE)), 1)
    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(CORECLOUDSHAPE1)), 2)


    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(BLUgtGREEN).And(GREENgtRED).And(NIR.gt(0.254)).And(BLU.gt(0.165)).And(NDVI.lt(0.40))), 2)


    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(BLUgtGREEN).And(BLU.gt(0.27)).And(GREEN.gt(0.21)).And(REDsubtractGREEN.lte(0.1)).And(NIR.gt(0.35))) , 2)

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(BLU.lt(0.13)).And(BLUgtGREEN).And(GREENgtRED).And(RED.lt(0.05)).And(BLUsubtractNIR.lt(-0.04))), 40)  # similar 2 cl 42 simplify

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(WETNESS.gt(5))), 8)  # only at this point to avoid confusion with shadows


    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(BLU.lt(0.13)).And(BLUgtGREEN).And(GREENgtRED).And(RED.lt(0.05)).And(BLUsubtractNIR.lt(0.04))), 42)

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(BLU.lt(0.14)).And(BLU.gt(0.10)).And(BLUgtGREEN).And(GREENgtRED).And(RED.lt(0.06)).And(NIR.lt(0.14)).And(((NIR).subtract(BLU)).lt(0.02))), 41)



    MyCOND = ((NIR.subtract(GREEN)).abs().lte(0.01)).add(BLUsubtractNIR.gte(0.01))
    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(BLUgtGREEN).And(GREENgtRED).And(NIR.gte(0.06)).And(MyCOND.gt(0))), 41)
    MyCOND = 0


    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(NDVI.lte(0.09)).And(NIR.lt(0.4)).And(GREENlteRED).And(REDlteNIR)), 35)

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(NDVI.lte(0.20)).And(NIR.gt(0.3)).And(growing14)), 34)

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(NDVI.gte(0.35)).And(BLUgteGREEN).And(REDsubtractGREEN.lt(0.04))), 21)


    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2).And(NDVI.gte(0.20)).And(REDsubtractGREEN.lt(0.05))), 30)

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_2)), 31)



    #-------------------------------------------------------------------------------------------------------------
    #----------------------  SECTION 3 : VEGETATION  -------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------

    MyCOND = (ndvi_3).And(NDVI.lt(th_RANGELAND))
    OUT = OUT.where(((OUT.eq(0)).And(MyCOND).And(NIR.gte(0.15))), 21)
    OUT = OUT.where(((OUT.eq(0)).And(MyCOND).And(NIR.lt(0.15))), 40)

    MyCOND = (ndvi_3).And(NDVI.lt(th_GRASS))
    OUT = OUT.where(((OUT.eq(0)).And(MyCOND).And(BLUlteNIR).And(NIR.lt(0.15))), 40)
    OUT = OUT.where(((OUT.eq(0)).And(MyCOND).And(BLUlteNIR)), 16)
    OUT = OUT.where(((OUT.eq(0)).And(MyCOND).And(BLU.gt(NIR))), 40)

    MyCOND = (ndvi_3).And(NDVI.lt(th_SHRUB))
    OUT = OUT.where(((OUT.eq(0)).And(MyCOND).And(NIR.gt(0.22))), 14)
    OUT = OUT.where(((OUT.eq(0)).And(MyCOND).And(NIR.gte(0.165))), 12)
    OUT = OUT.where(((OUT.eq(0)).And(MyCOND).And(NIR.lt(0.165))), 10)

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_3).And(NDVI.lt(th_TREES)).And(NIR.lt(0.30))), 11)
    OUT = OUT.where(((OUT.eq(0)).And(ndvi_3).And(NDVI.gt(th_TREES))), 9)

    OUT = OUT.where(((OUT.eq(0)).And(ndvi_3)), 13)

    return (OUT.select([0], ["Class"]).toByte())


    # SINGLE DATE CLASSIFICATION





#--------------------------------------------------------------------------------------------------------------
#  Phenology based synthesis functions
#--------------------------------------------------------------------------------------------------------------



class IMGeqTH:
    def __init__(self, TH):
        self.TH = TH
    def __call__(self, image):
        return image.eq(self.TH)

class IMGeqTHeqTHeqTH:
    def __init__(self, TH, TH1, TH2):
        self.TH = TH
        self.TH1 = TH1
        self.TH2 = TH2
    def __call__(self, image):
        return (image.eq(self.TH)).add(image.eq(self.TH1)).add(image.eq(self.TH2))


class IMGgteTHlteTH:
    def __init__(self, TH, TH1):
        self.TH = TH
        self.TH1 = TH1
    def __call__(self, image):
        return (image.gte(self.TH)).And(image.lte(self.TH1))



#--------------------------------------------------------------------------------------------------------------
#  Phenology based synthesis classification
#--------------------------------------------------------------------------------------------------------------


def PBS_classification(COLL):

    tot = (COLL.map(IMGgteTHlteTH(1, 43))).sum().divide(100)
    relTot = (COLL.map(IMGgteTHlteTH(3, 43))).sum().divide(100)

    #----------------------------------------------------------------------------------------------------------

    CLOUDS = ((COLL.map(IMGgteTHlteTH(1, 2))).sum()).divide(tot)
    tot = 0

    DARK_VEG = (COLL.map(IMGeqTH(40))).sum().divide(relTot)
    LOW_IL = (COLL.map(IMGeqTH(42))).sum().divide(relTot)
    DARK_SOIL = (COLL.map(IMGeqTHeqTHeqTH(35, 41, 43))).sum().divide(relTot)
    BRIGHT_SOIL = (COLL.map(IMGeqTH(34))).sum().divide(relTot)
    SPARSE = (COLL.map(IMGeqTH(30))).sum().divide(relTot)
    SOIL = (COLL.map(IMGeqTH(31))).sum().divide(relTot)
    BRIGHT_FOREST = (COLL.map(IMGeqTH(9))).sum().divide(relTot)
    FOREST = (COLL.map(IMGgteTHlteTH(10, 13))).sum().divide(relTot)
    DEGRADED_FOREST = (COLL.map(IMGeqTH(13))).sum().divide(relTot)
    SHRUB = (COLL.map(IMGgteTHlteTH(14, 16))).sum().divide(relTot)
    GRASS = (COLL.map(IMGgteTHlteTH(17, 21))).sum().divide(relTot)
    EVERGREEN_FOREST = (BRIGHT_FOREST.add(FOREST).add(DARK_VEG))
    WATER = (COLL.map(IMGgteTHlteTH(5, 8))).sum().divide(relTot)
    SNOW = (COLL.map(IMGeqTH(3))).sum().divide(relTot)
    DRY = SPARSE.add(SOIL).add(BRIGHT_SOIL).add(DARK_SOIL).add(LOW_IL)

    OUT = relTot.multiply(0).select([0], ["Class"]).toByte()

    OUT = OUT.where((OUT.eq(0)).And(SNOW.gte(80)), 2)

    # OUT=OUT.where( (OUT.eq(0)).And(CLOUDS.eq(100)),1)
    OUT = OUT.where((OUT.eq(0)).And(CLOUDS.gt(90)), 1)

    OUT = OUT.where((OUT.eq(0)).And(WATER.gt(80)), 8)
    OUT = OUT.where((OUT.eq(0)).And(WATER.gt(60)), 7)

    OUT = OUT.where((OUT.eq(0)).And((DARK_SOIL.add(LOW_IL)).gte(90)), 42)
    OUT = OUT.where((OUT.eq(0)).And(BRIGHT_SOIL.gte(90)) , 41)
    OUT = OUT.where((OUT.eq(0)).And(SOIL.gte(90)) , 35)
    OUT = OUT.where((OUT.eq(0)).And(SPARSE.gte(90)) , 36)
    OUT = OUT.where((OUT.eq(0)).And(DRY.gte(90)) , 34)

    OUT = OUT.where((OUT.eq(0)).And(DRY.add(SNOW).gte(95)) , 34)  # 06/10/2014
    OUT = OUT.where((OUT.eq(0)).And(DRY.add(SNOW).gte(85)).And(SPARSE.lt(10))  , 34)  # 06/10/2014

    GREEN = (EVERGREEN_FOREST.add(SHRUB).add(GRASS))

    OUT = OUT.where((OUT.eq(0)).And(FOREST.gt(90)), 10)
    OUT = OUT.where((OUT.eq(0)).And(FOREST.gt(50)).And(GREEN.gt(60)).And((WATER.add(SNOW).add(DARK_VEG).add(LOW_IL).add(GREEN)).gt(90)), 10)  # dark valley

    OUT = OUT.where((OUT.eq(0)).And(FOREST.gt(60)).And(EVERGREEN_FOREST.gt(80)), 11)
    OUT = OUT.where((OUT.eq(0)).And(FOREST.gt(70)).And(GREEN.eq(FOREST)), 11)
    OUT = OUT.where((OUT.eq(0)).And(FOREST.gt(50)).And((EVERGREEN_FOREST.add(SHRUB)).gt(80)).And(DRY.eq(0)), 12)

    OUT = OUT.where((OUT.eq(0)).And((GREEN.gt(90)).And(DRY.lt(5))).And(FOREST.lt(20)), 21)  # DEC open forest

    OUT = OUT.where((OUT.eq(0)).And((GREEN.eq(100)).And(FOREST.lt(5)).And(GRASS.gt(30))), 14)  # evergreen erbaceous

    OUT = OUT.where((OUT.eq(0)).And((BRIGHT_FOREST.add(DEGRADED_FOREST)).gt(50)).And(DRY.eq(0)), 13)  # evergreen shrub

    OUT = OUT.where((OUT.eq(0)).And(GREEN.gte(95)).And(FOREST.gte(40)).And(SHRUB.gt(40)).And(EVERGREEN_FOREST.gt(40))   , 15)  # almost evergreen

    # DECC CLOSE humid
    OUT = OUT.where((OUT.eq(0)).And(GREEN.gt(70)).And(SHRUB.gt(20)).And(FOREST.gt(10)).And((GRASS.add(SHRUB)).gt(30))   , 20)

    OUT = OUT.where((OUT.eq(0)).And(DRY.gt(90)) , 34)


    OUT = OUT.where((OUT.eq(0)).And((DRY.add(GRASS)).gt(80)).And(EVERGREEN_FOREST.eq(0)).And(GRASS.gte(DRY)).And(SHRUB.lte(5)) , 31)  #  bush + grass
    OUT = OUT.where((OUT.eq(0)).And((DRY.add(GRASS)).gt(80)).And(EVERGREEN_FOREST.eq(0)).And(DRY.gt(GRASS)).And(SHRUB.eq(0)) , 32)  # grass


    # EVG shrub
    OUT = OUT.where((OUT.eq(0)).And(GREEN.gt(85)).And(SHRUB.gt(70)).And(DRY.lt(5)) , 16)

    # DECC OPEN humid
    OUT = OUT.where((OUT.eq(0)).And(GREEN.gt(70)).And(GRASS.gt(30)).And(DRY.lt(25)) , 21)

    OUT = OUT.where((OUT.eq(0)).And(GREEN.gt(65)).And((GRASS.add(SHRUB)).gt(35)).And(DRY.lt(35)) , 26)  # DECIDE IF OPEN DRY or HUMID
    OUT = OUT.where((OUT.eq(0)).And(GREEN.gt(45)).And(GREEN.lt(60)).And(SHRUB.gte(15)).And(SHRUB.lt(40)).And(FOREST.eq(0)).And(DRY.gt(40)).And(DRY.lt(55)).And(GRASS.gt(15)).And(GRASS.lt(40)) , 25)

    #------------  SHRUB ------------------
    OUT = OUT.where((OUT.eq(0)).And(GREEN.gt(60)).And(FOREST.gt(0)).And(SHRUB.gt(10)) , 28)
    OUT = OUT.where((OUT.eq(0)).And(GREEN.gt(40)).And(SHRUB.add(GRASS).gt(30)) , 29)

    OUT = OUT.where((OUT.eq(0)).And(GREEN.gt(15)).And(FOREST.gt(0)) , 30)
    OUT = OUT.where((OUT.eq(0)).And(GREEN.gt(10)) , 31)

    OUT = OUT.where((OUT.eq(0)).And((DRY.add(WATER).add(SNOW)).gt(90)).And(WATER.gte(20)) , 6)
    OUT = OUT.where((OUT.eq(0)).And((GREEN.add(WATER)).gt(90)).And(WATER.gt(0)) , 9)

    return OUT
