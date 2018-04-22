# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 17:26:38 2018
@author: naitik
"""

"""
A simple example script to get all posts on a user's timeline.
Originally created by Mitchell Stewart.
<https://gist.github.com/mylsb/10294040>

Modified by Naitik shukla for Continous Assessment of Brand Watch Project

This Script will try te minimize work when restarting by not downloading already downloaded images in brand/images folder.
"""
import facebook
import requests
from time import time
import json,os,re
import urllib.request

def some_action(post,t,fil):
	""" Here you might want to do something with each post. E.g. grab the
	post's message (post['message']) or the post's picture (post['picture']).
	In this implementation we just print the post's created time.
	"""
	#print(post['created_time'])
	#print(post['message'])
	detail = graph.get_object(id=post['id'], fields="id,message,full_picture,shares,from,comments,likes.summary(true)")
	upd={}
	upd['post_id'] = detail['id']
	if 'message' in detail : upd['post_text']= detail['message']
	if 'shares' in detail : upd['share_count']= detail['shares']['count']
	if 'from' in detail: upd['from']={'id': detail['from']['id'],'name':detail['from']['name']}
	if 'full_picture' in detail :
		upd['photo_link']= detail['full_picture']			#updating html link also in json
		ct=re.search(".jpg", detail['full_picture']) or re.search(".png", detail['full_picture'])			#searching literal .jpg in html
		if ct:
			end=ct.span()[1]										#finding the found end position
			img_nm=detail['full_picture'][:end].split('/')[-1]	#extracting only image name from html
			if 'safe_image.php' in img_nm: img_nm= img_nm.split('%2F')[-1]
			path2Save = os.path.join(img_dest,img_nm)				#merging with path and filename
			if not os.path.exists(path2Save):
				urllib.request.urlretrieve(detail['full_picture'], path2Save)	#request image and save
			upd['local_dir']= "images/"+img_nm
	if 'likes' in detail : upd['num_likes']= detail['likes']['summary']['total_count']
	upd['post_time'] = post['created_time']
	if 'comments' in detail : upd['comments'] = [com for com in detail['comments']['data']]
	if 'story' in post : upd['story']=post['story']
	#fil.update(upd)
	fil[t]=upd
	print('loaded post number',t)

def write_file(posts,SKIP,t=1):
	#SKIP=True 		#If True will skip the pages of t variable
	#t=12					#change this if want to skip pages, only works when SKIP= True
	# Wrap this block in a while loop so we can keep paginating requests until
	# finished.
	while True:
	    try:
	        # Perform some action on each post in the collection we receive from
	        print('Started loading for post page:',t)
	        fil={}
	        if SKIP==True:
				      for i in range(1,t+1):
						       posts = requests.get(posts['paging']['next']).json()
						       print("Skipping page:",i)
				      SKIP=False
	        # Facebook.
	        [some_action(post,index,fil) for index,post in enumerate(posts['data'])] #calling function some_action to load 'fil' dictionary
	        tsp=str(time()).split('.')[0]
	        # Attempt to make a request to the next page of data, if it exists.
	        posts = requests.get(posts['paging']['next']).json()
	        #Write post page into json file
	        print('writitng file: fb_'+profile['name']+'-'+tsp+'_pg-'+str(t)+'.json')
	        with open('fb_'+profile['name']+'-'+tsp+'_pg-'+str(t)+'.json', 'w',encoding='utf-8') as outfile:
				      json.dump(fil, outfile)
	        t += 1
	    except KeyError:
	        # When there are no more pages (['paging']['next']), break from the
	        # loop and end the fetching.
	        print("exiting with finish loading")
	        break


if __name__=='__main()__':
	# You'll need an access token here to do anything.  You can get a temporary one
	# here: https://developers.facebook.com/tools/explorer/
	ACCESS_TOKEN = 'Provide your Access Token here'
	graph = facebook.GraphAPI(ACCESS_TOKEN) #handshake

	#change directory to work
	img_dest = os.path.expanduser("~\\Downloads\\brand\\images")
	if not os.path.exists(img_dest): os.makedirs(img_dest)
	os.chdir(img_dest)
	os.chdir("..")
	print("working directory: ",os.path.abspath(os.curdir))
	print("Image directory: ",img_dest)

	users = ['cocacolasg','mcdsg']	#Download and scrape data for Coca Cola sg page and Mcd sg
	for user in users:
		#get page information from facebook
		profile = graph.get_object(user)			#extract id for user from name
		posts = graph.get_connections(profile['id'], 'posts')	#fetch first 25 posts from page
		print("starting for user:",profile['name'])
		if user in []:
			write_file(posts,True,12)
		else:
			write_file(posts,False)

