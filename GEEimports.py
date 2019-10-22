#!/usr/bin/python

import time
import ee

def dumpclean(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print k
                dumpclean(v)
            else:
                if 'timestamp' in k:
                    print '%s : ' % k , time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(v/1000))
                else:
                    print '%s : %s' % (k, v)
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print v
    else:
        print obj

# ----------------------------------------------------------------------------------------
# algorithms
# ----------------------------------------------------------------------------------------

# Implements the Automatic Cloud Cover Assessment, with some changes
# http://landsathandbook.gsfc.nasa.gov/pdfs/ACCA_SPIE_paper.pdf
def calcConsACCA(img):
    f1 = img.select('B3').lt(0.08); # B3 below 0.08 is non-cloud
    f2 = img.normalizedDifference(['B2','B5']).gt(0.7); # (B2-B5)/(B2+B5) above 0.7 is non-cloud
    f3 = img.select('B6').gt(300); # B6 above this is non-cloud
  
    # Do not implement Pass Two here for simplicity, hence these
    # estimates are conservative (i.e., all ambiguous  is cloud)
    clouds = (f1.Or(f2).Or(f3)).Not();
  
    return img.addBands(clouds.rename(['cloud']));

def maskWater(image):
    #different water masks tried (MODIS LC, Hansen Global Forest change, NLCD and ESA LC):
#    water_modis = ee.Image('MCD12Q1/MCD12Q1_005_2001_01_01').select('Land_Cover_Type_1').eq(0);
#    water_hansen = ee.Image('UMD/hansen/global_forest_change_2015').select('datamask').eq(2)
#     if (US==1):
#         water = ee.Image('USGS/NLCD/NLCD2001').select('landcover').eq(11);
#     else:
#         water = ee.Image('ESA/GLOBCOVER_L4_200901_200912_V2_3').select('landcover').eq(210);
    #ultimately Fmask was best:
    water = image.select('fmask_water')
    return image.updateMask(water);

#Specifies a threshold for hue to estimate green pixels
# based on Ho et al. (2017), "Using Landsat to extend historical phytoplankton bloom records"
def calcGreenness(img):
    r = img.select(['B3']);
    g = img.select(['B2']);
    b = img.select(['B1']);
    I = r.add(g).add(b).rename(['I']);
    mins = r.min(g).min(b).rename(['mins']);
    H = mins.where(mins.eq(r),(b.subtract(r)).divide(I.subtract(r.multiply(3))).add(1) );
    H = H.where(mins.eq(g),(r.subtract(g)).divide(I.subtract(g.multiply(3))).add(2) );
    H = H.where(mins.eq(b),(g.subtract(b)).divide(I.subtract(b.multiply(3))) );
    
    Hthresh = H.lte(1.6)
    return Hthresh;