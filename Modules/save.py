print("Module save imported")
import pickle

### AUN NO FUNCIONA ###

def save(allobjects, fil="Tmp.inv"):
    print("Saving?")
    try:
        os.remove(fil)
    except:
        pass
    for obj in allobjects:
        with open(fil, "wb") as output:
            pickle.dump(obj, output)

def load(allobjects, fil="Tmp.inv"):
    with open(fil, "rb") as inpt:
        print(pickle.load(inpt))