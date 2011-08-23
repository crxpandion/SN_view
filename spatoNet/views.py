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

color_dict = { 'N' : '#E30038', #red
               'U' : '#E30038', #red
               'M' : '#00c224', #green
               'Q' : '#808080'} #grey

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
    numToDisplay = 15 
    l_fset = formset_factory( LinkForm, extra = numToDisplay)
    old_entries = grabOldLinkForms(request, ID)
    form = l_fset(initial=old_entries)
    Icount = len(old_entries)
    print Icount
    def errorHandle(error, ID):
        param = {  'error' : error,
                   'form' : l_fset(initial= grabOldLinkForms(request, ID)),
                   'me' : me, 
                   'network' : network, }
        if Icount > 0:
            param['ready'] = True
        param.update(csrf(request))
        return render_to_response('inputNetwork.html', param, context_instance=RequestContext(request) )
    def refreshParams():
         formset = formset_factory(LinkForm, extra=numToDisplay)
         old_entries = grabOldLinkForms(request,ID)
         param = { 'form': formset(initial=old_entries), 'me': People.objects.get(user_ID = ID),'network' : network }
         if len(old_entries) > 0:
            param['ready'] = True
         param.update(csrf(request))
         return render_to_response('inputNetwork.html', param, context_instance=RequestContext(request)) 

    if request.method == 'POST':
        if "delete" in request.POST:
            if request.POST['delete'] != 'None':
                deleteLinkEntry( LinkEntry.objects.get( link_ID = request.POST['delete']) )
            return refreshParams()
        fset = l_fset(request.POST) 
        if fset.is_valid():
            for i, f in enumerate(fset.cleaned_data):
                if f and not LinkEntry.objects.filter(a = f['a'], b = f['b'], c = f['c'], user_ID = ID ): # if f is not empty and f does not exist... 
                                                                                                          # also edge case: when they input 'Me'
                    #check if it is an edit of initial data
                    if i < Icount:
                        l = old_entries[i] # edited linkEntry
                        LinkEntry.objects.filter(link_ID = l['id']).delete()
                        le = LinkEntry( a = f['a'], b = f['b'], c = f['c'], user_ID = me, link_ID = l['id'] )
                    else:
                        le = LinkEntry( a = f['a'], b = f['b'], c = f['c'], user_ID = me )
                    le.save()
                    le.makeLinks()
            return refreshParams()    
        else:
            error = u'you must enter valid Names.'
            return errorHandle(error, ID)
    else:
        param = {'form': form, 
                 'me': me, 
                 'network' : network, }
        if Icount > 0:
            param['ready'] = True
        param.update(csrf(request))
        return render_to_response('inputNetwork.html', param, context_instance=RequestContext(request))

def viewNetwork(request, ID):
    param = {}
    param['jsonNet'] = generateJson(ID)
    return render_to_response('viewNetwork.html', param, context_instance=RequestContext(request))

################### HELPER FUNCTIONS #######################

def deleteLinkEntry(link):
    # the borker shoudl be the only one that requires a chekc to delte teh children
    # #a = l.cleanSplits( l.a.split(' ', 2) )
    #     b = l.cleanSplits( l.b.split(' ', 2) )
    #     #list_of_friends = l.c.split(',')
    #     broker = People.objects.filter(first_Name = b[0], last_Name = b[1])
    broker_children = LinkEntry.objects.filter( a = link.b )
    if broker_children:
        for child in broker_children:
            child.delete()
    link.delete()
    
    
#def searchForLinkEntryContaining():
    
    

def generateJson(ID):
    jsString = []
    links = Link.objects.filter(parent = ID)
    peeps = makeUniquePeopleList(links)
    for p in peeps:
        d = {}
        d['id'] = str(p.user_ID)
        d['name'] = str(p.first_Name) + ' ' + str(p.last_Name)
        d['data'] = {}
        adj = []
        ls = links.filter(u = p.user_ID)
        for l in ls:
            print l.link_type
            adjDict = {}
            adjDict['nodeTo'] = str(l.v.user_ID)
            adjDict['data'] = {'$color' : color_dict[l.link_type] } 
            if l.link_type == 'Q':
                print 'yes'
                adjDict['data']['$ignore'] = 'true'
                adjDict['data']['$type'] = 'line'
            adj.append(adjDict)
        d['adjacencies'] = adj
        jsString.append(d)
        #print json.dumps(jsString, indent = 4)
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

        