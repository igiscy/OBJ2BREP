import math
import os
import time
from os import name
import shapefile
import shapely
from lxml import etree, objectify
import xml.etree.ElementTree as et
import itertools as it
import copy
import tkinter as tk
from Geometry3D import *



def main(mesh):
    core = "http://www.opengis.net/citygml/3.0"
    bldg = "http://www.opengis.net/citygml/building/3.0"
    trans = "http://www.opengis.net/citygml/transportation/3.0"
    gml = "http://www.opengis.net/gml/3.2"
    gen = "http://www.opengis.net/citygml/generics/3.0"
    xlink = "http://www.w3.org/1999/xlink"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    grp = "http://www.opengis.net/citygml/cityobjectgroup/3.0"
    vers = "http://www.opengis.net/citygml/versioning/3.0"
    igis = "https://www.geomatics.ncku.edu.tw"
    mdq = "http://standards.iso.org/iso/19157/-2/mdq/1.0"
    mcc = "http://standards.iso.org/iso/19115/-3/mcc/1.0"
    gco = "http://standards.iso.org/iso/19115/-3/gco/1.0"
    cit = "http://standards.iso.org/iso/19115/-3/cit/1.0"
    mrl = "http://standards.iso.org/iso/19115/-3/mrl/1.0"

    nsmap = {
        'core': core,
        'bldg' : bldg,
        'grp': grp,
        'trans': trans,
        'gen': gen,
        'gml': gml,
        'xlink': xlink,
        'xsi': xsi,
        'igis':igis,
        'mdq': mdq,
        'mcc': mcc,
        'gco': gco,
        'cit':cit,
        'mrl': mrl,
        'vers': vers
    }
    # Add branch
    attr_qname = etree.QName(xsi, 'schemaLocation')
    print('['+time.strftime("%H:%M:%S", time.localtime())+'] '+'CityGML Converter Start ...')
    cityModel = etree.Element("{%s}CityModel" % core, attrib={attr_qname: 'https://www.geomatics.ncku.edu.tw ADE.xsd'}, nsmap=nsmap)
    cityObject = etree.SubElement(cityModel, "{%s}cityObjectMember" % core)
    building = etree.SubElement(cityObject, "{%s}Building" % igis)
    lod1solid = etree.SubElement(building, "{%s}lod1Solid" % core)
    solid = etree.SubElement(lod1solid, "{%s}Solid" % gml, srsName="EPSG:28992", srsDimension="3")
    exterior = etree.SubElement(solid, "{%s}exterior" % gml)
    Shell = etree.SubElement(exterior, "{%s}Shell" % gml)
    for t in range(0, len(mesh),1):
        if (len(mesh[t])<3):
            continue
        else:
            surfaceMember = etree.SubElement(Shell, "{%s}surfaceMember" % gml)
            surface = etree.SubElement(surfaceMember, "{%s}Surface" % gml)
            patches = etree.SubElement(surface, "{%s}patches" % gml)
            PolygonPatch = etree.SubElement(patches, "{%s}PolygonPatch" % gml)
            exterior = etree.SubElement(PolygonPatch, "{%s}exterior" % gml)
            LinearRing = etree.SubElement(exterior, "{%s}LinearRing" % gml)
            posList = etree.SubElement(LinearRing, "{%s}posList" % gml)
            posList.text = ""
            for k in range(len(mesh[t])-1,-1,-1):
                posList.text = posList.text + " " +str(mesh[t][k])
                posList.text = posList.text.replace('[', '')
                posList.text = posList.text.replace(']', '')
                posList.text = posList.text.replace(',', '')

    et = etree.ElementTree(cityModel)
    outFile = open('C:\\Users\\C.YANG\\Desktop\\Random3Dcity_2015-03-11\\Test3.gml', 'wb')
    et.write(outFile, xml_declaration=True, encoding='utf-8', pretty_print=True)
    print('['+time.strftime("%H:%M:%S", time.localtime())+'] '+'Transformation Done !')

def normalvector(plane, accuracy, threshold):
    ux, uy, uz = u = [round(plane[1][0]-plane[0][0],accuracy),round(plane[1][1]-plane[0][1],accuracy),round(plane[1][2]-plane[0][2],accuracy)]
    vx, vy, vz = v = [round(plane[2][0]-plane[0][0],accuracy),round(plane[2][1]-plane[0][1],accuracy),round(plane[2][2]-plane[0][2],accuracy)]
    x, y, z = cross = [uy*vz-uz*vy, uz*vx-ux*vz, ux*vy-uy*vx]
    if ((x**2+y**2+z**2)**0.5 == 0):
        ux, uy, uz = u = [round(plane[1][0]-plane[0][0],threshold),round(plane[1][1]-plane[0][1],threshold),round(plane[1][2]-plane[0][2],threshold)]
        vx, vy, vz = v = [round(plane[2][0]-plane[0][0],threshold),round(plane[2][1]-plane[0][1],threshold),round(plane[2][2]-plane[0][2],threshold)]
        x, y, z = cross = [uy*vz-uz*vy, uz*vx-ux*vz, ux*vy-uy*vx]
    if ((x**2+y**2+z**2)**0.5 != 0):
        vector = [i / ((x**2+y**2+z**2)**0.5) for i in cross]
        return vector


def edgegeneration(plane):
    edge1 = [plane[0][0], plane[0][1], plane[0][2],plane[1][0], plane[1][1], plane[1][2]]
    edge2 = [plane[1][0], plane[1][1], plane[1][2],plane[2][0], plane[2][1], plane[2][2]]
    edge3 = [plane[2][0], plane[2][1], plane[2][2],plane[0][0], plane[0][1], plane[0][2]]
    return edge1,edge2, edge3


def parasingmesh(plane, accuracy = 30, threshold= 30):
    vector = normalvector(plane, accuracy, threshold)
    edge1 = edgegeneration(plane)[0]
    edge2 = edgegeneration(plane)[1]
    edge3 = edgegeneration(plane)[2]
    meshinformation = [vector, edge1, edge2, edge3]
    if (vector != None):
        return meshinformation


def classifier(planelist, accuracy = 6): #分類器子程序
    vectorlist = []
    for i  in planelist:
        if([round(num,accuracy) for num in i[0]] not in vectorlist):
            vectorlist.append([round(num,accuracy) for num in i[0]])
    classifylist = []
    for i in vectorlist:
        edgelist=[]
        for t in planelist:
            if (i == [round(num,accuracy) for num in t[0]]):
                edgelist.append([t[1], t[2], t[3]])
        classifylist.append(edgelist)
    return classifylist


def detector(classifierlist): #偵測器子程序，偵測與篩選顛倒的向量
    replanelist=[]
    for singlevector in classifierlist:
        temp_classifierlist = copy.deepcopy(singlevector)
        for i in range(0,len(singlevector),1):
            for j in range(0,len(singlevector[i]),1):
                for t in range(0,len(singlevector),1):
                    for k in range(0,len(singlevector[t]),1):
                        if ((singlevector[i][j][0] == singlevector[t][k][3])and(singlevector[i][j][1] == singlevector[t][k][4])and(singlevector[i][j][2] == singlevector[t][k][5])and(singlevector[i][j][3] == singlevector[t][k][0])and(singlevector[i][j][4] == singlevector[t][k][1])and(singlevector[i][j][5] == singlevector[t][k][2])):
                            if ((singlevector[i][j] in temp_classifierlist[i])and(singlevector[t][k] in temp_classifierlist[t])):
                                temp_classifierlist[i].remove(singlevector[i][j])
                                temp_classifierlist[t].remove(singlevector[t][k])
        replanelist.append(temp_classifierlist)
    return replanelist


def arranger(replanelist): #排列器子程序，將篩選後的向量重新按照連接性排列
    finalcoorlist = []
    groundlist = []
    for singlevector in replanelist:
        edgelist = []
        for t in range(0,len(singlevector),1):
            for k in range(0,len(singlevector[t]),1):
                edgelist.append(singlevector[t][k])
                if(singlevector[t][k][2] == 0 and singlevector[t][k][5] == 0):
                    groundlist.append(singlevector[t][k])
        temp_edgelist = copy.deepcopy(edgelist)
        for q in range(0,len(edgelist),1):
            if (len(temp_edgelist) == 0):
                break
            replanecoorlist = []
            for j in range(0,len(temp_edgelist),1):
                if (len(temp_edgelist) == 0):
                    break
                if (j == 0):
                    replanecoorlist.append([temp_edgelist[j][0],temp_edgelist[j][1],temp_edgelist[j][2]])
                    replanecoorlist.append([temp_edgelist[j][3],temp_edgelist[j][4],temp_edgelist[j][5]])
                    temp_edgelist.remove(temp_edgelist[j])
                for t in range(0,len(edgelist),1):
                    if (len(temp_edgelist) == 0):
                        break
                    lengthindex = len(replanecoorlist)-1
                    if ((replanecoorlist[lengthindex][0] == edgelist[t][0])and(replanecoorlist[lengthindex][1] == edgelist[t][1])and(replanecoorlist[lengthindex][2] == edgelist[t][2])):
                        if ((edgelist[t][3] == replanecoorlist[0][0])and(edgelist[t][4] == replanecoorlist[0][1])and(edgelist[t][5] == replanecoorlist[0][2])):
                            if (edgelist[t] in temp_edgelist):
                                temp_edgelist.remove(edgelist[t])
                            break
                        '''if (((round((edgelist[t][3]-replanecoorlist[lengthindex-1][0])*(edgelist[t][4]-edgelist[t][1]),2)) == round(((edgelist[t][4]-replanecoorlist[lengthindex-1][1])*(edgelist[t][3]-edgelist[t][0])),2)) and ((round((edgelist[t][5]-replanecoorlist[lengthindex-1][2])*(edgelist[t][3]-edgelist[t][0]),2)) == (round((edgelist[t][3]-replanecoorlist[lengthindex-1][0])*(edgelist[t][5]-edgelist[t][2]),2)))):
                            replanecoorlist.remove([replanecoorlist[lengthindex][0],replanecoorlist[lengthindex][1],replanecoorlist[lengthindex][2]])'''
                        replanecoorlist.append([edgelist[t][3],edgelist[t][4],edgelist[t][5]])
                        if (edgelist[t] in temp_edgelist):
                            temp_edgelist.remove(edgelist[t])
                        continue
            if (len(replanecoorlist) != 0):
                finalcoorlist.append(replanecoorlist)
    return finalcoorlist

def GetMesh():
    data = open('your OBJ file path (.obj)','r')
    contents = data.readlines()
    ##讀取所有向量點
    n=0
    point_array = []
    face_index_array = []
    for array in contents:
        point = []
        if(array.split(' ')[0] == 'v'):
            n = n+1  #插入OBJ索引號
            x = float(array.split(' ')[1])
            y = float(array.split(' ')[2])
            z = float(array.split(' ')[3].replace('\n',''))
            if (z == -0.0):
                z = 0.0
            point = [n, x, y, z]  #擷取三角面的向量點
            point_array.append(point)
        face_index = []
        if (array.split(' ')[0] == 'f'):
            face_index = [array.split(' ')[1], array.split(' ')[2], array.split(' ')[3]]
            face_index_array.append(face_index)
    mesh_array = []
    parsing_mesh_array = []
    for face_index in face_index_array:
        mesh = []
        for index in face_index:
            for point in point_array:
                if (index == str(point[0])):
                    mesh.append([point[1], point[2], point[3]])
                    break
        mesh_array.append(mesh)
        if (parasingmesh(mesh) != None):
            parsing_mesh_array.append(parasingmesh(mesh))
    classifierlist = classifier(parsing_mesh_array,2)
    detectorlist = detector(classifierlist)
    finalplane = arranger(detectorlist)
    return finalplane

main(GetMesh())