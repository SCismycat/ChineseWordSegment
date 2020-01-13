#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/1/13 23:55
# @Author  : Leslee

class TrainNgram():

    def __init__(self,N=1):
        self.N = N
        self.word_dict = {}
        self.trans_dict = {}

    # 训练N-gram参数
    def train(self,train_path,word_dict_path,trans_dict_path):
        print('Start training..')
        self.word_dict['<BEG>'] = 0
        self.trans_dict['<BEG>'] = {}

        with open(train_path,'r',encoding='utf-8') as f:
            for sentence in f.readlines():
                self.word_dict['<BEG>'] += 1 #BEG用于填充第0个词。所以，每个句子都会出现，因此+1
                sentence = sentence.strip()
                sentence = sentence.split(' ')
                sentence_list = []
                for idx, words in enumerate(sentence):
                    if words != '':
                        sentence_list.append(words)

                for idx, words in enumerate(sentence_list):
                    if words not in self.word_dict.keys():
                        self.word_dict[words] = 1
                    else:
                        self.word_dict[words] += 1
                    # 词频统计
                    # 构造2-gram，并统计频率
                    if idx == 0:
                        # 句首，填充
                        words1, words2 = '<BEG>',words
                    elif idx == len(sentence_list)-1:
                        words1,words2 = words,'<BEG>'
                    # 非句首，构造b-gram
                    else:
                        words1,words2 = words, sentence_list[idx+1]
                    # 统计当前词后面所接词语出现的次数
                    if words not in self.trans_dict.keys():
                        self.trans_dict[words1] = {}# 构造一个嵌套的字典
                    if words2 not in self.trans_dict[words1]:
                        self.trans_dict[words1][words2] = 1 # words1后面没出现过word2，赋值1
                    else:
                        self.trans_dict[words1][words2] += 1 # 否则 +1
            self.save_model(self.word_dict,word_dict_path)
            self.save_model(self.trans_dict,trans_dict_path)

    def save_model(self,word_dict,model_path):
        with open(model_path,'w',encoding='utf-8') as writer:
            writer.write(str(word_dict))

def main():
    train_p = '../data/train.txt'
    word_dict_path = '../model/word_dict.model'
    trans_dict_path = '../model/trans_dict.model'
    trainer = TrainNgram(1)
    trainer.train(train_p,word_dict_path,trans_dict_path)

main()

