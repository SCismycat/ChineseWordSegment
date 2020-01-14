#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/1/14 15:09
# @Author  : Leslee
import math

class BiDirectNgram(object):

    def __init__(self,worddict_path="../model/word_dict.model",transdict_path = '../model/trans_dict.model'):
        self.word_dict = {} # 词频词典
        self.trans_dict = {} # 每个词后面接的词的计数
        self.word_counts = 0 # 语料库总词数
        self.word_types = 0 # 语料库中词种数
        self.worddict_path = worddict_path
        self.transdict_path = transdict_path


    '''加载模型'''
    def load_model(self, model_path):
        f = open(model_path, 'r',encoding='utf-8')
        a = f.read()
        word_dict = eval(a)
        f.close()
        return word_dict

    def init_model(self,worddict_path,transdict_path):
        self.word_dict = self.load_model(worddict_path)
        self.trans_dict = self.load_model(transdict_path)
        self.word_counts = sum(self.word_dict.values())
        self.word_types = len(self.word_dict)

    # 计算句子生成概率
    def compute_likelihood(self,seg_list):
        p = 0
        # 连乘转连加
        for pos, words in enumerate(seg_list):
            if pos < len(seg_list)-1:
                if pos < len(seg_list)-1:
                    # 乘以后面词的条件概率
                    word1, word2 = words,seg_list[pos+1]
                    if word1 not in self.trans_dict.keys():
                        # 拉普拉斯平滑
                        p += math.log(1.0/self.word_counts)
                    else:
                        number1,number2 = 1.0,self.word_counts
                        for key in self.trans_dict[word1]:
                            if key == word2:
                                # 在字典树中发现word2，加上对应的频率。
                                number1 += self.trans_dict[word1][word2]
                            number2 += self.trans_dict[word1][key]

                        p += math.log(number1/number2)
            if (pos ==0 and words !='<BEG>') or (pos == 1 and seg_list[0] == '<BEG>'):
                if words in self.word_dict.keys():
                    p += math.log((float(self.word_dict[words])+ 1.0)/(self.word_types+self.word_counts))
                else:
                    p += math.log(1.0/(self.word_types+self.word_counts))
        return p

    # 最大前向匹配
    def max_forward_cut(self,sentence):
        cutList = []
        index = 0
        MaxLen = self.MaxLen

        while(index<len(sentence)):
            matched = False
            for i in range(MaxLen,0,-1):
                candidate_words = sentence[index:index+i]
                if candidate_words in self.word_dict:
                    cutList.append(candidate_words)
                    matched = True
                    break
            # 没匹配上
            if not matched:
                i = 1
                cutList.append(sentence[index])# index只加1，即单字成词。
            index += i
        return cutList

    # 最大后向匹配
    def max_backward_match(self,sentence):
        cutList = []
        # maxLen = len(max(self.word_dict,key=len))
        maxLen = 6
        index = len(sentence)
        while index >0:
            matched = False
            for i in range(maxLen,0,-1):
                tmp = (i+1) # 记录偏移量
                candidate_words = sentence[index-tmp:index]
                if candidate_words in self.word_dict:
                    cutList.append(candidate_words)
                    matched =True
                    break

            if not matched:
                tmp = 1
                cutList.append(sentence[index-1])
            index -= tmp

        return cutList[::-1]

    def cut_words(self,sentence):
        seg_list1 = self.max_forward_cut(sentence)
        seg_list2 = self.max_backward_match(sentence)
        seg_list = []

        # differ1和differ2分别记录句子序列不同的部分，使用n-gram消歧
        differ_list1 = []
        differ_list2 = []

        # pos记录当前字位置
        # cur记录第几个词
        pos1 = pos2 = 0
        cur1 = cur2 = 0
        while 1:
            if cur1 == len(seg_list1) and cur2 == len(seg_list2):
                break
            if pos1 == pos2:
                if len(seg_list1[cur1]) == len(seg_list2[cur2]):
                    pos1 += len(seg_list1[cur1])
                    pos2 += len(seg_list2[cur2])
                    # 当词序列不同时，使用n-gram做概率
                    if len(differ_list1) > 0:
                        differ_list1.insert(0,seg_list[-1])
                        differ_list2.insert(0,seg_list[-1])
                        if cur1 < len(seg_list1) - 1:
                            differ_list1.append(seg_list1[cur1])
                            differ_list2.append(seg_list2[cur2])
                        p1 = self.compute_likelihood(differ_list1)
                        p2 = self.compute_likelihood(differ_list2)
                        if p1 > p2:
                            differ_list = differ_list1
                        else:
                            differ_list = differ_list2
                        differ_list.remove(differ_list[0])

                        if cur1 < len(seg_list1) -1:
                            differ_list.remove(seg_list1[cur1])
                        for words in differ_list:
                            seg_list.append(words)
                        differ_list2 = []
                        differ_list1 = []

                    seg_list.append(seg_list1[cur1])
                    cur1 += 1
                    cur2 += 1
                elif len(seg_list1[cur1]) > len(seg_list2[cur2]):
                    differ_list2.append(seg_list2[cur2])
                    pos2 += len(seg_list2[cur2])
                    cur2 += 1
                else:
                    differ_list1.append(seg_list1[cur1])
                    pos1 += len(seg_list1[cur1])
                    cur1 += 1
            else:
                # pos1不同，而结束的位置相同，两个同时向后滑动
                if pos1 + len(seg_list1[cur1]) == pos2 + len(seg_list2[cur2]):
                    differ_list1.append(seg_list1[cur1])
                    differ_list2.append(seg_list2[cur2])
                    pos1 += len(seg_list1[cur1])
                    pos2 += len(seg_list2[cur2])
                    cur1 += 1
                    cur2 += 1
                elif pos1 + len(seg_list1[cur1]) > pos2 + len(seg_list2[cur2]):
                    differ_list2.append(seg_list2[cur2])
                    pos2 += len(seg_list2[cur2])
                    cur2 += 1
                else:
                    differ_list1.append(seg_list1[cur1])
                    pos1 += len(seg_list1[cur1])
                    cur1 += 1

        return seg_list
