searchstring = 'count'
for alg in QgsApplication.processingRegistry().algorithms():
    # only return the algids that contain the searchstring
    # remove that if statement to print all algid's
    if searchstring in alg.id(): 
        print(alg.id())