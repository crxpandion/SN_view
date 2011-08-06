import os
from django.forms.formsets import formset_factory
from django.template import Context, loader, RequestContext
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.context_processors import csrf
from spatoNet.models import People, Link, LinkForm, NameForm, LinkEntry
from xml.dom import minidom
from StringIO import StringIO
from zipfile import ZipFile
import random
import json

# Create your views here.

color_dict = { 'N' : '#808080', 'U': '#E30038', 'M' :'#00c224', }

def inputName(request):
    def errorHandle(error):
        form = NameForm()
        return render_to_response('inputName.html', {
                   'error' : error,
                   'form' : form,
        })
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            me = People( first_Name = request.POST['first_Name'].strip().title(), last_Name = request.POST['last_Name'].strip().title())
            me.save()
            return HttpResponseRedirect("/inputNetwork/%d/" % me.user_ID)
        else:
            return errorHandle( u'Please Input your First and Last Name' )
    else:
        form = NameForm() # An unbound form
        param = {'form': form}
        param.update(csrf(request))
        return render_to_response('inputName.html', param, context_instance=RequestContext(request))


def inputNetwork(request, ID):
    network = '/viewNetwork/%s/' % ID
    me = People.objects.get(user_ID = ID)
    numToDisplay = 25 
    l_fset = formset_factory( LinkForm, extra = numToDisplay)
    old_entries = grabOldLinkForms(request, ID)
    form = l_fset(initial=old_entries)
    Icount = len(old_entries)
    def errorHandle(error, ID):
        param = {  'error' : error,
                   'form' : l_fset(initial= grabOldLinkForms(request, ID)),
                   'me' : me, 
                   'network' : network, }
        if Icount > 0:
            param['ready'] = True
        param.update(csrf(request))
        return render_to_response('inputNetwork.html', param, context_instance=RequestContext(request) )

    if request.method == 'POST':
 #       if "delete" in request.POST:
 #          LinkEn
        fset = l_fset(request.POST) 
        if fset.is_valid():
            for f in fset.cleaned_data:
                if f:
                    print f
                if f and not LinkEntry.objects.filter(a = f['a'], b = f['b'], c = f['c'], user_ID = ID ): # if f is not empty and f does not exist... 
                                                                                                          # also edge case: when they input 'Me'
                    le = LinkEntry( a = f['a'], b = f['b'], c = f['c'], user_ID = me )
                    le.save()
                    le.makeLinks()
            formset = formset_factory(LinkForm, extra=numToDisplay)
            old_entries = grabOldLinkForms(request,ID)
            param = { 'form': formset(initial=old_entries), 'me': People.objects.get(user_ID = ID),'network' : network }
            if len(old_entries) > 0:
                param['ready'] = True
            param.update(csrf(request))
            return render_to_response('inputNetwork.html', param, context_instance=RequestContext(request)) 
        else:
            error = u'you must enter valid Names.'
            return errorHandle(error, ID)
    else:
        param = {'form': form, 'me': me, 'network' : network, }
        if Icount > 0:
            param['ready'] = True
        param.update(csrf(request))
        return render_to_response('inputNetwork.html', param, context_instance=RequestContext(request))

def viewNetwork(request, ID):
    param = {}
    param['jsonNet'] = generateJson(ID)
    return render_to_response('viewNetwork.html', param, context_instance=RequestContext(request))

################### HELPER FUNCTIONS #######################



def generateJson(ID):
    jsString = []
    links = Link.objects.filter(parent = ID)
    peeps = makeUniquePeopleList(links)
    for p in peeps:
        d = {}
        d['id'] = str(p.user_ID)
        d['name'] = str(p.first_Name) + ' ' + str(p.last_Name)
        #d['data'] = {}
        adj = []
        ls = links.filter(u = p.user_ID)
        for l in ls:
            adjDict = {}
            adjDict['nodeTo'] = str(l.v.user_ID)
            adjDict['data'] = {'$color' : color_dict[l.link_type] } 
            adj.append(adjDict)
        d['adjacencies'] = adj
        jsString.append(d)
    return json.dumps(jsString, separators=(',',':'))


def makeUniquePeopleList(l):
    master = []
    for links in l:
        master.append(links.u)
        master.append(links.v)
    keys = {}
    for p in master:
        keys[p] = 1
    return keys.keys()

#def linkEntryToLinkTransform

def grabOldLinkForms(request, user_ID):
    link_forms = LinkEntry.objects.filter(user_ID = user_ID)
    l = []
    for link_f in link_forms:
        dic = {}
        dic['a'] = link_f.a.title()
        dic['b'] = link_f.b.title()
        dic['c'] = link_f.c.title()
        dic['id'] = link_f.link_ID
        l.append(dic)
    return l


def processLinkForm(f, user_ID):
    I = []
    I.append(f['a'].strip().title().split())
    I.append(f['b'].strip().title().split())
    I.append(f['c'].strip().title().split())
    for j in I:
        if len(j) > 0:
            firstN = j[0]
            if len(j) < 2 :
                j.append('')
            lastN = j[1]
            createPerson(firstN, lastN)
        else:
            j.append('')
            j.append('')
    broker = I[0]
    contact = I[1]
    friends = I[2]

#if you havent been introduced to your broker yet then we create a  link to do so. 
    if (not (int(user_ID) == int(People.objects.get(first_Name = broker[0], last_Name = broker[1]).user_ID))) and (not (Link.objects.filter(u = People.objects.get(user_ID = user_ID), v = People.objects.get(first_Name = broker[0], last_Name = broker[1])))):
        Link(parent = People.objects.get(user_ID = user_ID),
            u   = People.objects.get(user_ID = user_ID),
            v   = People.objects.get(first_Name = broker[0], last_Name = broker[1]),).save()
        Link(parent = People.objects.get(user_ID = user_ID),
            u   = People.objects.get(first_Name = broker[0], last_Name = broker[1]),
            v   = People.objects.get(user_ID = user_ID),).save()


    
    Link(parent = People.objects.get(user_ID = user_ID),
            u   = People.objects.get(first_Name = broker[0], last_Name = broker[1]),
            v   = People.objects.get(first_Name = contact[0], last_Name = contact[1]),).save()
    Link(parent = People.objects.get(user_ID = user_ID),
            u   = People.objects.get(first_Name = contact[0], last_Name = contact[1]),
            v   = People.objects.get(first_Name = broker[0], last_Name = broker[1]),).save()
    if not friends[0] == '':
        Link(parent = People.objects.get(user_ID = user_ID),
                u   = People.objects.get(first_Name = contact[0], last_Name = contact[1]), 
                v   = People.objects.get(first_Name = friends[0], last_Name = friends[1]),).save()
        Link(parent = People.objects.get(user_ID = user_ID),
                u   = People.objects.get(first_Name = friends[0], last_Name = friends[1]),
                v   = People.objects.get(first_Name = contact[0], last_Name = contact[1]),).save()

    return ''
             
def createPerson(first_name, last_name = ''):
    if not People.objects.filter(first_Name = first_name, last_Name = last_name):
        People(first_Name = first_name, last_Name = last_name).save()

def loadLinks(ID):
    Links = LinkEntry.objects.filter(user_ID = ID)

    l = []
    if Links:
        print 'links'
        for link in Links:
            d = {}
            d['a'] = link.a
            d['b'] = link.b
            d['c'] = link.c
            l.append( d)
    return l



######################## OLD CODE ########################


def getNetwork(request, ID):
    in_memory = StringIO()
    zip = ZipFile(in_memory, "a")
    #probably want to pass in structures to writing functions 
    zip.writestr("links.xml", str(writeLinksXML(Link.objects.filter(parent = ID))))
    zip.writestr("nodes.xml", str(writeNodesXML(Link.objects.filter(parent = ID))))
    zip.writestr("document.xml", str(writeDocXML(ID)))
    # slices ???


    # fix for Linux zip files read in Windows
    for file in zip.filelist:
        file.create_system = 0    
        
    zip.close()

    response = HttpResponse(mimetype="application/zip")
    response["Content-Disposition"] = "attachment; filename=your_network.zip.spato"
    
    in_memory.seek(0)    
    response.write(in_memory.read())
    
    return response






def writeLinksXML(Links):
    lxml = minidom.Document()
    lxmlRoot = lxml.createElement("links")
    peeps = makeUniquePeopleList(Links)
    for p in peeps:
        src = lxml.createElement("source")
        src.setAttribute('index', str(p.user_ID))
        ls = Links.filter(u = p.user_ID)
        for l in ls:
            target = lxml.createElement("target")
            target.setAttribute('index', str(l.v.user_ID))
            target.setAttribute('weight', '1')
            src.appendChild(target)
        lxmlRoot.appendChild(src)
    ''' 
    for l in Links:
        src = lxml.createElement("source")
        src.setAttribute('index', str(l.u.user_ID))
        target = lxml.createElement("target")
        target.setAttribute('index', str(l.v.user_ID))
        src.appendChild(target)
        lxmlRoot.appendChild(src)
    '''    
    lxml.appendChild(lxmlRoot)
    return lxml.toxml()

def writeNodesXML(Links):
    peeps = makeUniquePeopleList(Links)

    nxml = minidom.Document()
    nxmlRoot = nxml.createElement("nodes")
    for p in peeps:
        node = nxml.createElement("node")
        node.setAttribute('id', str(p.user_ID))
        node.setAttribute('name', str(p.first_Name) + ' ' +  str(p.last_Name))
        node.setAttribute('location', str(random.random()) + ',' + str(random.random()))
        node.setAttribute('strength', '1')
        nxmlRoot.appendChild(node)
    nxml.appendChild(nxmlRoot)
    return nxml.toxml()

def writeDocXML(ID):
    me = People.objects.get(user_ID = ID)
    xml = minidom.Document()
    xmlRoot = xml.createElement("document")
    title = xml.createTextNode(me.first_Name + " " + me.last_Name + '\'s ' + 'network')
    tit = xml.createElement("title")
    tit.appendChild(title)
    xmlRoot.appendChild(tit)
    nodes = xml.createElement("nodes")
    nodes.setAttribute("src", 'nodes.xml')
    xmlRoot.appendChild(nodes)
    links = xml.createElement("links")
    links.setAttribute("src", 'links.xml')
    xmlRoot.appendChild(links)
    #slices ???
    xml.appendChild(xmlRoot)
    return xml.toxml()
