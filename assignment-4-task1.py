'''
Assignment 4: Task 1
'''

import nltk
import re
import random
import json
import sys,glob
import os.path
import csv

'''function to tokenize and tag a sentence with it's associated a parts of speech '''
def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

'''function to replace unneccesary patterns from sentences given in each of the relations file in order to tag a pos'''
def remove_unnecessary(pattern,phrase):
    for pat in pattern:
        list1=re.findall(pat,phrase)
        for i in range(len(list1)):
            phrase=phrase.replace(list1[i], " ")
    return phrase

'''selects a output file name to place in the run folder of task1'''
def select_outputfilename(filepath):
    outputfile=''
    filepath=filepath.strip("a4_data//")
    filepath=filepath.strip("\\")
    filepath=filepath.replace("."," ")
    for i in range(len(filepath)):
        if filepath[i]==" ":
            break
        else:
            outputfile=outputfile+filepath[i]
    return outputfile 

'''writes the "Original Sentence", "List of POS" and "Misclassified Entities" of a given file'''
def generate_output(filename,facts_list):
    savepath='task1/runs/'
    filepath = os.path.join(savepath, filename+".txt")
    with open(filepath,'wt', encoding='utf8') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        tsv_writer.writerow(['               Original Sentence             ', '                   List of POS      ', '       Misclassified Entity    '])
        for fact in facts_list:
            tsv_writer.writerow(fact)
            
''' The below mentioned function is written in order to analyze the outputs in the report. '''

'''writes the no of filtered sentences per relation along with the avg no of '''
'''misidentified entities per sentence'''
def generate_filtered_sentences_per_relation(list1_of_facts):
    savepath='task1/runs/'
    filepath = os.path.join(savepath, "relation_filtered_sentences.txt")
    with open(filepath,'wt', encoding='utf8') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        tsv_writer.writerow(['   Relation    ', '   Number of filtered sentences ','          Average no of misclassified entities per sentences'])
        for fact in list1_of_facts:
            tsv_writer.writerow(fact)


    
def main():
    #random.seed(10)
    ''' list of patterns to be removed from each of the sentences given in each of the relation'''
    pattern = ['\|.*?\]\]','\[\[','/','\(','\)',"\'","\'\'",'\[','\]']
    '''list to append each of the given relations and the no of filtered sentences'''
    list1_of_facts=[]
    for filepath in glob.glob('a4_data/*'):
        FilesFound=False
        match = re.search(r"/*.json", filepath)
        if match is not None:
            FilesFound=True
        if(FilesFound):
            outputfile=select_outputfilename(str(filepath))
            '''Load each of the json files'''
            with open(filepath, 'r') as js:
                json_data = json.load(js)
                
                '''dictionary to store the number of misclassified sentences per relation'''
                mydict2=dict()
                
                '''dictionary to store parts of speech of each of the sentence '''
                '''with keys as the random sentence number of a relation and values'''
                '''as the pos for that sentence     '''
                mydict3=dict()
                
                '''list to append everything of a relation as Original_Sentences, '''
                '''List of POS for these sentence and any misclassified entities of these '''
                '''sentence'''
                list_of_facts=[]   
                
                '''a counter to store the number of misclassified entities per sentence'''
                m=0
                
                for i in range(100):
                    randomsamples=random.randrange(0,len(json_data),1)
                    '''dictionary to store all the misclassified entities of each sentences'''
                    mydict=dict()
                    
                    text=json_data[randomsamples]['sentence']
                    original_sent=remove_unnecessary(pattern,text)
                    sentence_pos_tags=preprocess(original_sent)
                    for postags in sentence_pos_tags:
                        if str(randomsamples) in mydict3.keys():
                            mydict3[str(randomsamples)].append(str(postags[0])+"/"+str(postags[1]))
                        else:
                            mydict3[str(randomsamples)]=[str(postags[0])+"/"+str(postags[1])]
                    
                    '''match a pattern to identify the entities that are labelled in the given sentences'''
                    '''here result is a list of all such entities'''
                    result = re.findall(r"\[\[.*?\|", text)
                    #print(len(result))
                    for j in range(len(result)):
                        
                        '''each of the entities are cleaned removing unnecessary patterns'''
                        result[j]=result[j].strip("[[")
                        result[j]=result[j].strip("|")
                        result[j]=result[j].strip(" ")
                        res=""
                        intermediate=result[j]
                        for z in range(len(intermediate)):
                            if intermediate[z]==" ":
                                break
                            else:
                                res=res+intermediate[z]
                        for postags in sentence_pos_tags:
                            if (postags[0]==res):
                                '''if the first entry of each such entities are anything other(Such '''
                                '''as Adjectives, Verbs, Digits, etc.) rather than being Noun and Noun Phrase,'''
                                '''then such entities in a sentence are counted'''
                                if(postags[1]!='NNP' and postags[1]!='NN' and postags[1]!='NNS' and postags[1]!='NNPS'):
                                    m=m+1
                                    if str(randomsamples) in mydict.keys():
                                        mydict[str(randomsamples)].append(result[j])
                                        mydict2[str(randomsamples)].append(result[j])
                                    else:
                                        mydict[str(randomsamples)]=[result[j]]
                                        mydict2[str(randomsamples)]=[result[j]]
                                else:
                                    break
                        
                        
                    '''commented line prints all the misclassified entities in each of the '''
                    '''sentences for each of the relational files'''
                    #print(mydict)
                    
                    
                    '''list that appends everything of a relation as Original_Sentences, List '''
                    '''of POS for these sentence and any misclassified entities of these sentence'''
                    
                    for i in range(len(mydict3[str(randomsamples)])):
                        if i>0:
                            l1=len(json_data[randomsamples]['sentence'])
                            l2=' '
                            for j in range(l1):
                                l2+=' '
                            l3=' '
                            if (str(randomsamples) in mydict.keys()):
                                len_dict=len(mydict[str(randomsamples)])
                                if i< len_dict:
                                    list_of_facts.append([l2 , mydict3[str(randomsamples)][i], mydict[str(randomsamples)][i]])
                                else:
                                    list_of_facts.append([l2,mydict3[str(randomsamples)][i], l3])
                            else:
                                l3=' '
                                list_of_facts.append([l2,mydict3[str(randomsamples)][i], l3])
                                
                        else:
                            if str(randomsamples) in mydict.keys():
                                list_of_facts.append([json_data[randomsamples]['sentence'],mydict3[str(randomsamples)][i], mydict[str(randomsamples)][i]])
                            else:
                                l3=' '
                                list_of_facts.append([json_data[randomsamples]['sentence'],mydict3[str(randomsamples)][i], l3])
                    
                    '''generates output of task 1 in a text file'''
                    generate_output(outputfile,list_of_facts)
                    
                
                '''A identifier q to compute the average number of misclassified entities'''
                q=m/100
                
                '''list that appends each of the given relations and the no of filtered sentences'''
                list1_of_facts.append([outputfile,"               "+str(len(mydict2)), "                         "+str(q)])
                
                '''generates output as a text file in order to analyze the output'''
                generate_filtered_sentences_per_relation(list1_of_facts)
                
main()