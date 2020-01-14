#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/1/14 10:12
# @Author  : Leslee
import math
class MaxNgramCut(object):

    def __init__(self):
        self.word_dict = {} # 记录单词的概率
        self.word_dict_count = {} #记录单词的词频
        self.trans_dict = {} # 记录2-gram的概率
        self.trans_dict_count = {} # 记录2-gram的词频
        self.max_word_len = 0 # 最长词的长度
        self.all_freq = 0 # 所有词的词频总和
        word_count_path = "../model/word_dict.model"
        word_trans_path = '../model/trans_dict.model'
        self.init(word_count_path, word_trans_path)
    # 加载预训练模型
    def load_model(self, model_path):
        f = open(model_path, 'r', encoding='utf-8')
        a = f.read()
        word_dict = eval(a)
        f.close()
        return word_dict

    def init(self,word_count_path,word_trans_path):
        self.word_dict_count = self.load_model(word_count_path)
        self.all_freq = sum(self.word_dict_count.values()) #所有词的词频
        self.max_word_len = len(max(self.word_dict_count.keys(),key=len))
        for key in self.word_dict_count:
            # 单词的概率，每个词出现的概率/总词数
            self.word_dict[key] = math.log(self.word_dict_count[key] / self.all_freq)
        # 再计算转移概率
        Trans_dict = self.load_model(word_trans_path)
        for pre_word, post_info in Trans_dict.items():
            # post_word是二元的第二个字，count是第一个字后跟第二个字的次数
            for post_word, count in post_info.items():
                word_pairs = pre_word+ ' ' + post_word
                self.trans_dict_count[word_pairs] = float(count)
                # 如果转移概率里面的key的词，在word_dict中
                if pre_word in self.word_dict_count.keys():
                    # 这里计算的是，p(wi-1,wi)/p(wi-1)
                    self.trans_dict[post_word] = math.log(count/self.word_dict_count[pre_word])
                else:
                    # 如果不在词表中，表示这个词在第一个词的词表中没出现。把单词出现的概率，给到转移概率。
                    self.trans_dict[post_word] = self.word_dict[post_word]
    # 针对没出现的词，用平滑算法
    def get_unknown_word_prob(self,word):
        return math.log(1.0/(self.all_freq**len(word)))

    # 获取候选词概率
    def get_candidate_word_prob(self,word):
        if word in self.word_dict.keys():
            prob = self.word_dict[word]
        else:
            prob = self.get_unknown_word_prob(word)
        return prob
    # 获取候选词的转移概率
    def get_candidate_word_trans_prob(self,pre_word,post_word):
        trans_word = pre_word + " " + post_word
        # 如果该二元词法在二元词频中
        if trans_word in self.trans_dict_count.keys():
            # 计算，二元词的词频/第一个词的词频
            trans_prob = math.log(self.trans_dict_count[trans_word]/self.word_dict_count[pre_word])
        else:
            trans_prob = self.get_candidate_word_prob(post_word)
        return trans_prob

    # 寻找node的最佳前驱节点，寻找所有可能的前驱片段
    def get_best_pre_node(self,sentence,node,node_state_list):
        # node的长度，作为自适应长度
        max_node_len = min([node,self.max_word_len])
        pre_node_list = [] # 前驱节点列表

        # 获得所有的前驱片段，记录累加概率,
        for segment_len in range(1,max_node_len+1):
            if segment_len == 3:
                print("")
            seg_start_node = node - segment_len # 取一个句子片段的索引
            segment = sentence[seg_start_node:node] #获取片段
            pre_node = seg_start_node # 取该片段，则记录对应的前驱节点
            if pre_node == 0:
                # 如果前驱片段开始节点，是序列的开始节点。概率是<BEG>转移到当前次词的概率
                segment_prob = self.get_candidate_word_trans_prob("<BEG>",segment)
                pre_pre_word = "<BEG>"
            else:
                # 不是序列开始节点，计算二元概率
                # 获取该片段的前一个词
                pre_pre_node = node_state_list[pre_node]["pre_node"]
                pre_pre_word = sentence[pre_pre_node:pre_node]
                segment_prob = self.get_candidate_word_trans_prob(pre_pre_word,segment)
            # 前驱节点的概率累加值
            pre_node_prob_sum = node_state_list[pre_node]["prob_sum"]
            # 当前node一个候选的累加概率值
            candidate_prob_sum = pre_node_prob_sum + segment_prob
            candidate_prob_word = pre_pre_word + segment
            pre_node_list.append((pre_node,candidate_prob_sum,candidate_prob_word))
        # 找到最大的候选概率值
        (best_pre_node,best_prob_sum,best_prob_word) = max(pre_node_list,key=lambda d: d[1])

        return best_pre_node,best_prob_sum,best_prob_word
    # 主函数
    def cut_main(self,sentence):
        sentence = sentence.strip()
        # 初始化
        node_state_list = [] # 记录节点的最佳前驱，index是位置信息
        init_state = {}
        init_state['pre_node'] = -1 # 前一个节点
        init_state['prob_sum'] = 0 # 当前的概率和
        init_state['cur_word'] = "" # 当前的词
        node_state_list.append(init_state)
        for node in range(1,len(sentence)+1):
            # 寻找最佳前驱，记录当前最大的概率累加值
            if node == 4:
                print("")
            (best_pre_node, best_prob_sum,best_prob_word) = self.get_best_pre_node(sentence,node,node_state_list)
            # 添加到队列
            cur_node = {}
            cur_node["pre_node"] = best_pre_node
            cur_node["prob_sum"] = best_prob_sum
            cur_node["cur_word"] = best_prob_word
            node_state_list.append(cur_node)
        # 获取最优路径，从后向前
        best_path = []
        node = len(sentence)
        best_path.append(node)
        while True:
            pre_node = node_state_list[node]["pre_node"]
            if pre_node == -1:
                break
            node = pre_node
            best_path.append(node)
        best_path.reverse()

        # 构建切分
        word_list = []
        for i in range(len(best_path)-1):
            left = best_path[i]
            right = best_path[i+1]
            word = sentence[left:right]
            word_list.append(word)
        return word_list

    def cut(self,sentence):
        return self.cut_main(sentence)
def test():
    cuter = MaxNgramCut()
    sentence = "我励志成为自然语言处理专家"
    seg_sentence = cuter.cut(sentence)
    print("original sentence: " , sentence)
    print("segment result: ", seg_sentence)

test()