print("Module save imported")
import pickle

### AUN NO FUNCIONA ###

def save(allobjects, cabls, fil="Tmp.inv"):
    print("Saving?")
    try:
        os.remove(fil)
    except:
        pass
    print(allobjects)
    with open(fil, "wb") as output:
        pickle.dump((allobjects,cabls), output)

def load(fil="Tmp.inv"):
    global Switch
    print(classes)
    with open(fil, "rb") as inpt:
        allobj, cables = pickle.load(inpt)
        print(allobj)
        print(cables)
        for obj in allobj:
            obj.load()
        for cable in cables:
            cable.load()