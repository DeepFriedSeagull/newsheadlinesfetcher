import face_recognition
import os
from PIL import Image

#https://medium.com/@ageitgey/machine-learning-is-fun-part-4-modern-face-recognition-with-deep-learning-c3cffc121d78

# Script for testing face_recognition lib.
# Using one picture as reference and testing all the other one..


# This is our reference
picture_of_reference = face_recognition.load_image_file( os.path.join("Pictures","fillon","Fillon_0.jpg") )
reference_encoding = face_recognition.face_encodings(picture_of_reference)[0]


candidate_path = os.path.join("Pictures","fillon")
images_test = [os.path.join(candidate_path, f)  for f in os.listdir(candidate_path) if os.path.isfile(os.path.join(candidate_path, f))]

for image_test in images_test:

	unknown_picture = face_recognition.load_image_file( image_test )
	unknown_faces_encoding = face_recognition.face_encodings(unknown_picture)
	print( "*** {}: ".format( image_test ), end='') 

	candidateFound = False;

	# There can be more than recognized face in one picture
	for i in range (len(unknown_faces_encoding)):
		# Let's compare with our reference
		results = face_recognition.compare_faces([reference_encoding], unknown_faces_encoding[i])

		if True in results:
			print("Reference is the picture")
			candidateFound = True

	if candidateFound is False:
		print("ERROR REFERENCE NOT FOUND !!!")



# images_test = ["test.jpg", "test2.jpg", "test3.jpg"]