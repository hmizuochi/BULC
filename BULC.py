#make sure all maps contain null (base mask) value -99.
import numpy as np; import copy; import matplotlib.pyplot as plt; from sklearn.metrics import confusion_matrix
ROW=3340; COL=3340; PNGDIR='PNG'
with open('base.raw',mode='rb') as fp: #base forest(F)/non-forest(NF) map at the beginning
    initial=np.fromfile(fp,np.int16,-1)
Prior0=np.where(initial==0,0.6,initial); Prior0=np.where(initial==1,0.4,Prior0) #Prior probability for F(0). fix 0.6/0.4 according to Cardille & Fortin (2016).
Prior1=np.where(initial==1,0.6,initial); Prior1=np.where(initial==0,0.4,Prior1) #Prior probability for NF(1)
FNF=copy.deepcopy(Prior0)
ref=copy.deepcopy(initial)
with open('nullratio_new.txt',mode='r') as fp: #the csv file that includes each FNF map and its null ratio (due to cloud etc) along integation order, like "${YR}${MON}${DAY}_LandsatFNF_label.raw,${NULLRATIO}"
    lines = fp.readlines()
for l in lines:
    if l.split(",")[1].split("_")[0]=='19990215':
        continue
    else:
  with open(l.split(",")[1].replace('\n',''),mode='rb') as fp:
            new=np.fromfile(fp,np.int16,-1)
        if new[new!=-99].shape[0]==0: # new is all null. no update for ref, therefore ref cannot be all-null.
            Post1=copy.deepcopy(Prior1); Post0=copy.deepcopy(Prior0)
        elif np.unique(new).shape[0]==2 or np.unique(ref).shape[0]==2: #new or ref only contains one category other than null (-99)
            Post1=copy.deepcopy(Prior1); Post0=copy.deepcopy(Prior0)
            ref=copy.deepcopy(new)
        else: #new and ref contains full categories (-99,0,1)
            cmat=confusion_matrix(ref,new,labels=[-99,0,1])[1:3,1:3] #please make sure the map always contains null (base mask).
            likelihood=[(cmat[1][1]+1)/(cmat[1].sum()+2),(cmat[0][1]+1)/(cmat[0].sum()+2),(cmat[1][0]+1)/(cmat[1].sum()+2),(cmat[0][0]+1)/(cmat[0].sum()+2)] #NF->NF(100%), F->NF, NF->F(0%), F->F         
            tmp1=np.where(new==1,likelihood[0]*Prior1,new)
            tmp0=np.where(new==1,likelihood[1]*Prior0,new)
            tmp1=np.where(new==0,likelihood[2]*Prior1,tmp1)
            tmp0=np.where(new==0,likelihood[3]*Prior0,tmp0)
            Post1=copy.deepcopy(tmp1/(tmp0+tmp1)); Post0=copy.deepcopy(tmp0/(tmp0+tmp1)); Post1=np.where(new==-99,Prior1,Post1); Post0=np.where(new==-99,Prior0,Post0)
            ref=copy.deepcopy(new)

        FNF[Post0>=Post1]=0; FNF[Post0<Post1]=1; FNF=np.where(Post0==-99,np.nan,FNF)
        #plt.imshow(FNF.reshape(ROW,COL),cmap="summer") for journal figure
        plt.figure(figsize=(4,4),dpi=120); plt.imshow(FNF.reshape(ROW,COL),cmap="autumn_r"); plt.savefig(PNGDIR+"/BULC_"+l.split(",")[0]+"_Constraint90.png"); plt.close()
        with open("BULC_"+l.split(",")[0]+"_Constraint90.raw",'wb') as fp:
            FNF.reshape(ROW,COL).astype('int16').tofile(fp)
        with open("BULC_"+l.split(",")[0]+"_Constraint90_prob.raw",'wb') as fp:
            Post1.reshape(ROW,COL).astype('float32').tofile(fp)
        Prior0=copy.deepcopy(Post0); Prior1=copy.deepcopy(Post1)
        Prior0=np.where(((Prior0<0.1) & (Prior0>=0)),0.1,Prior0); Prior0=np.where((Prior0>0.9),0.9,Prior0) #activate here if you use constraint.
        Prior1=np.where(((Prior1<0.1) & (Prior1>=0)),0.1,Prior1); Prior1=np.where((Prior1>0.9),0.9,Prior1)

        #tmp=np.where(Prior0==-99,np.nan,Prior0) #plt.imshow(tmp.reshape(ROW,COL)) #tmp=np.where(Prior1==-99,np.nan,Prior1) #plt.imshow(tmp.reshape(ROW,COL))
