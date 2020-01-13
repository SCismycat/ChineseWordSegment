#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/1/13 19:48
# @Author  : Leslee

class ChiCutWords:

    def __init__(self,data_path,MaxLen):
        self.word_dict = self.load_words(data_path)
        self.MaxLen = MaxLen

    def load_words(self,dict_path):
        wordVocab = []
        with open(dict_path,'r',encoding='utf-8') as f:
            for line in f.readlines():
                wordVocab += line.strip().split(' ')
        return wordVocab

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

    # 最大双向匹配算法
    def max_biward_cut(self,sentence):
        # 如果正反一样，随便返回
        # 如果分词数量不同，返回分词数量少的。另外返回单字较少的那个
        forward_cutList = self.max_forward_cut(sentence)
        backward_cutList = self.max_backward_match(sentence)
        count_forward = len(forward_cutList)
        count_backward = len(backward_cutList)
        # 计算单字数量
        def compute_single_word(word_list):
            num = 0
            for word in word_list:
                if len(word) == 1:
                    num += 1
            return num
        if count_forward == count_backward:
            if compute_single_word(forward_cutList)>compute_single_word(backward_cutList):
                return backward_cutList
            else:
                return forward_cutList
        elif count_backward> count_forward:
            return forward_cutList
        else:
            return backward_cutList

def main():
    dict_path = "../userdict/dict.txt"
    MaxLen = 6
    sent = "我励志成为自然语言处理专家"
    Chi = ChiCutWords(dict_path,MaxLen)
    # print(Chi.max_forward_cut(sent))
    print(Chi.max_backward_match(sent))
main()