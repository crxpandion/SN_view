from django.db import models
from django import forms

# Create your models here.

class People(models.Model):
    first_Name = models.CharField(max_length=20)
    last_Name = models.CharField(max_length=20, blank = True)
    user_ID = models.AutoField(primary_key=True)
    def clean(self):
        data = self.cleaned_data
        data['first_Name'] = data['first_Name'].strip().title()
        data['last_Name'] = data['last_Name'].strip().title()
        return data
    
class LinkEntry(models.Model):
    user_ID = models.ForeignKey(People)
    link_ID = models.AutoField(primary_key=True)
    a = models.CharField(max_length=30)
    b = models.CharField(max_length=30)
    c = models.CharField(max_length=200)

    def save(self, *args, **kwargs):

        if self.a.split()[0] == 'Me':
           me = People.objects.get(user_ID = self.user_ID.user_ID)
           self.a = me.first_Name + ' ' + me.last_Name
        super(LinkEntry, self).save(*args, **kwargs)
 
    def cleanSplits(self, s):
        if len(s) < 2:
            s.append('')
        return s

    def createPerson(self, first_name, last_name = ''):
        if not People.objects.filter(first_Name = first_name, last_Name = last_name):
            People(first_Name = first_name, last_Name = last_name).save()

    def cleanAndChopNames(self):    
        d = {}
        broken_a = self.cleanSplits(self.a.split(' ', 2))
        broken_b = self.cleanSplits(self.b.split(' ', 2))
        list_of_friends = self.c.split(',')
        print broken_a[0]
        if not broken_a[0] == 'Me': 
            d['broker'] = {'first_name' : broken_a[0], 'last_name' : broken_a[1] }
        else:
            me = self.user_ID 
            d['broker'] = {'first_name' : me.first_Name, 'last_name' : me.last_Name }
        d['contact'] = {'first_name' : broken_b[0], 'last_name' : broken_b[1] }
        d['friends'] = []
        for friend in list_of_friends:
            broken_friend = self.cleanSplits(friend.strip().split(' ', 2))
            d['friends'].append( { 'first_name' : broken_friend[0], 'last_name' : broken_friend[1] } )
        return d

    def makeLinks(self):
        ppl_dict = self.cleanAndChopNames()
        self.createPerson(ppl_dict['broker']['first_name'], ppl_dict['broker']['last_name'])
        self.createPerson(ppl_dict['contact']['first_name'], ppl_dict['contact']['last_name'])
        friends = self.makeFriends(ppl_dict['friends'])
        broker = People.objects.get(first_Name = ppl_dict['broker']['first_name'], last_Name = ppl_dict['broker']['last_name'])
        contact = People.objects.get(first_Name = ppl_dict['contact']['first_name'], last_Name = ppl_dict['contact']['last_name'])
        me = self.user_ID
        #M_P = self.user_ID.user_ID == broker.user_ID
        if (self.user_ID != broker.user_ID): 
            if (not Link.objects.filter(u = me, v = broker)):
                Link(parent = me, link_type = 'N', entry = self, u = me, v = broker, ).save()
            # if (not Link.objects.filter(u = me, v = contact)):
            #     Link(parent = me, link_type = 'Q', entry = self, u = me, v = broker, ).save() # as you now know this person
            Link(parent = me, link_type = 'U', entry = self, u = broker, v = contact, ).save()
           # Link(parent = me, link_type = 'N', entry = self, u = me, v = contact,).save()
        else:
            Link(parent = me, link_type = 'N', entry = self, u = me, v = contact, ).save() #should it be M ??
        if len(friends) > 0:
            for p in friends:
                Link(parent = me, link_type = 'M', entry = self, u = contact, v = p, ).save() #should check to see if your already connected to p ..
                Link(parent = me, link_type = 'Q', entry = self, u = me, v = p,).save()
    def makeFriends(self, friend_dict):
        friends = []
        for person in friend_dict:
            if not person['first_name'] == '': 
                self.createPerson(person['first_name'], person['last_name'])
                friends.append(People.objects.get(first_Name = person['first_name'], last_Name = person['last_name']))
        return friends
  
class Link(models.Model): 
    LINK_CHOICES = (
            ('M', 'I Introduced Them'),
            ('U', 'You Introduced Them'),
            ('N', 'Normal'),
            ('Q', 'Normal')
            )
    parent = models.ForeignKey(People)
    entry = models.ForeignKey(LinkEntry)
    link_type = models.CharField(max_length=1, choices=LINK_CHOICES)
    u =  models.ForeignKey(People, related_name='+')
    v =  models.ForeignKey(People, related_name='+')

class LinkForm(forms.Form):
    a = forms.CharField(max_length=30)
    b = forms.CharField(max_length=30)
    c = forms.CharField(max_length=200, required = False)
    id = forms.IntegerField(required = False)

    def clean(self):
        data = self.cleaned_data
        data['a'] = data['a'].strip().title()
        data['b'] = data['b'].strip().title()
        data['c'] = data['c'].strip().title()
        return data

class NameForm(forms.Form):
    first_Name = forms.CharField(max_length = 30)
    last_Name = forms.CharField(max_length = 30)

    def clean(self):
        data = self.cleaned_data
        data['first_Name'] = data['first_Name'].strip().title()
        data['last_Name'] = data['last_Name'].strip().title()
        return data


