import face_recognition
import os
from PIL import Image

picture_of_fillon = face_recognition.load_image_file( os.path.join("Pictures","fillon","Fillon_0.jpg") )
face_of_fillon_encoding = face_recognition.face_encodings(picture_of_fillon)[0]

# my_face_encoding now contains a universal 'encoding' of my facial features that can be compared to any other picture of a face!

# images_test = ["test.jpg", "test2.jpg", "test3.jpg"]

candidate_path = os.path.join("Pictures","fillon")
images_test = [f for f in os.listdir(candidate_path) if os.path.isfile(os.path.join(candidate_path, f))]

for image_test in images_test:
	unknown_picture = face_recognition.load_image_file( image_test )
	unknown_faces_encoding = face_recognition.face_encodings(unknown_picture)


	print( "*** {}  ***".format( image_test ) ) 
	# print( "There is {} face(s) in the image".format(len(unknown_faces_encoding)))

	candidateFound = False;
	for i in range (len(unknown_faces_encoding)):
		# print ("Face num: {}".format(i))
		# Now we can see the two face encodings are of the same person with `compare_faces`!
		results = face_recognition.compare_faces([face_of_fillon_encoding], unknown_faces_encoding[i])

		if True in results:
			print("Fillon is the picture")
			candidateFound = True

		# if False in results:
		# 	print("There at least somebody is unknown")

	if candidateFound is False:
		print("ERROR $CANDIDATE$ NOT FOUND !!!")
