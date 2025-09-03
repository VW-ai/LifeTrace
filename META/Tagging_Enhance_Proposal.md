### 首先是数据的存储可能需要升级

1. 不能把calendar和notion当作同一种事件
    
    Calendar是标杆，Notion是context。我们本质上做的就是，把calendar当作query，去做搜索，notion就是我们的文本库。无论如何，这个用calendar 去找context。
    
    不当作同一种事件来存储的一个重要因素是，Notion有很重要的parent block，child block的事件。
    
    我们对来自Notion的存储就必须要注重，一定要存下来parent ←→ Child之间的关系，这个tree-like structure 对我们的后续很重要。
    
2. 本质上我们是需要用Calendar → Notion的context（这一步其实没有太多invovle content的，可以只用time 去match 我们的block（created time) 
    
    在notion 存储的时候，我们需要keep track of the child block that we have updated within 24 hrs （follow by most recent edited time) 
    
    1. 我们会单独存newly updated 的block ID，逻辑上，是我们存一个树。这里，我目前这个block是A，然后A的child block B 新增了一个child blockC ，那么我们的block B的存储里会写（C被edited, and edited 的时间)。同时，block A的存储里会写（B被edited， and edited 的time，这里如果有多个block 被edited，取最新时间）。
    2. 因为是树，是有A→ B→ C的这种结构的。
    3. 我们的agent只会去处理出现在这里的block id
    
    这么设计的思路是，我们可以快速从很多page很多block的内容中locate到需要读取的内容。而不是让AI去scan through 一整个database。
    
    那我们是如何做这样个当天用的tree的？机制如下：
    
    1. 首先，先去清空前一天的newly updated 的那些block ID
    2. 然后我们在每天我们执行page scan update from notion的时候，这里我们是一个全局的对notion的scan，或者什么机制，总之，我们会提取出所有edited 在最近24hr（或者20hr，etc）的block，然后把这几个block的parent会给一路提上去，变成一个链路。然后我们把链路交汇处merge 一下变成tree。最后就是一个page 一个简单tree。
    3. Agent在去notion的时候，就只会用calendar event尝试match这些notion event。并且在match后，还会通过AI 去基于Notion生成based on 我们notion content（如果有对应的话）的文本（长度限制在30-100 words），这个generated content 会被存储为`abstract` . abstract 会被用到
        1. embedding generation
        2. 用户展示上（e.g.最近五天花费时间最多的单一活动，鼠标放在活动名上，就是会展示这个abstract。
3. 至于如果这个tag没有，最好是基于title，以及我们的global context（这里就要用到我们的embedding)

### 在tag这个事情上，是不是可以适当利用information retrieval

embedding可以帮助我们在global下找到对应的context。R@100够高就行，剩下的交给AI。

这里我们的存储很简单，就是notion 的block_id，这个block在我们数据库里的id，和一个embedding。

我们只对notion的”leaf blocks”的`abstract`做embedding。也就是ignore heading啥的那些，那些我们不直接生成（但是我们生成leaf的时候会把所有的上面几层layer的block的内容放进text里）

然后当我们需要做global 的context finding 时，就可以用一个title 的embedding去找到对应的几个leaf block，再由大模型去reason，这些个match到的对不对。（高级一点的话我们甚至可以build 一个proximity graph based on embedding，但这个记为高级TODO就好了。）