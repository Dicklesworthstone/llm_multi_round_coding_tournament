
# LLM Multi-Round Coding Tournament

## The Simple Version

For the past month or so, I've had a lot of success with a simple but powerful technique for using LLM models to help me write code. I'll give the same exact coding prompt to multiple different models.

There are 4 models I think make sense to use for this currently, but really you should think of it as the "3 or 4 best models you have access to." In my case, these are:

- o1-pro
- o3-mini-high
- Claude 3.7 Sonnet
- Grok3

The technique I would generally use would be to first pick two models, usually Claude 3.7 Sonnet and Grok3 (both with "thinking" mode enabled to use chain-of-thought, which is better for coding). Then I would take the response given by each model (the whole response, not just the code) and paste it as a second message in the conversation with the other model:

> OK I asked the same exact question to a competing LLM and it gave me back the response below. Which one of these is better, your version or the competing version? Can you think of smart ways to combine the best of both worlds?

Then, I would take this second response from each model, and do the same things, but with this preamble message:

> I asked the other LLM the same question, to compare and then combine the best of both versions. See its response below. Which do you think is better?

This simple trick very often gave much better code than either model individually. The only annoying thing is the additional time it takes, but for critically important functions, it's been worth it for me.

## Taking it to the Next Level

This got me thinking about how this idea could be taken to its natural conclusion: a bunch of smart LLMs all duking it out together in a competitive yet collaborative fashion, but not as a one-shot deal, but in a multi-stage "tournament" style, where each LLM would have multiple chances to synthesize the learnings of its AI brethren to find more tricks and inspirations for further improvements and optimizations.

I quickly realized that if I naively followed the same exact approach but with 4 models instead of 2, I would quickly run into a combinatorial explosion of having to show each model each other model's response, and so on with the follow up responses.

Thus, I decided to instead put ALL the responses during each round in a single markdown file for submission. I also took some liberties with when I would create a new "conversation" with each model to clear out the context window fully and get them to start with a fresh state of mind.

## A Good Test Problem

Now, in order to make any of this interesting and worthwhile, we need a worthy problem. That is, a simple problem with a pretty straightforward and an obvious correct answer wouldn't show off the power of this method, because all the models would hopefully quickly converge on the right answer.

I decided that the best kind of problem would be one that is a bit messy and which didn't have a single right answer or even a "best approach," but which admitted many possible approaches. I finally settled on the problem of trying to "fix" an invalid markdown table.

That is, given a markdown document as input, the function should find all the "attempted tables" in the document (carefully skipping over without change any non-table contents in the file), and then for each one it finds, first determine if the table is valid. If it is valid, then it should skip over it without any change.

If it's invalid, then we want to make the least invasive changes possible to make it valid, while best capturing the original "intent" of the tabular data.

I included 3 examples of invalid tables that arose naturally through the use of the `html2text` library in Python when applied to HTML files from SEC's EDGAR filing system of public company filings. It's no surprise that any automated conversion tool would likely struggle with these tables— they are *nasty*.

That is, they are filled with bizarre and ugly practices, like merged cells that span multiple columns, spurious empty columns, columns created just for the purpose of holding a "$" sign or even a ")" for negative numbers, and tables that contain footnotes.

All of these elements violate basic assumptions of markdown's table formatting rules, which emphasize simplicity. At the same time, there's really no good reason that the vast majority of such tables couldn't be re-imagined in a way that would include the same information but in a way that works well enough with markdown— at least so they don't appear as a jumbled mess.

Obviously, there are lots of ways to go about this problem, with lots of different and potentially conflicting (or complementary) heuristics and strategies one could try. First of all, what's the most robust and reliable way to even detect a potential table? We certainly want to avoid false positives, because the last thing we want to do is mess up existing content which is not a table and which is already displayed correctly.

And once we think we've found a table, how should we go about diagnosing what is wrong with it? And once we think we know what's wrong with it, what's the best way to fix each tabular ailment? Once we've made a 'fix,' we really need to check it again to make sure that our fix didn't introduce yet another problem that needs to be fixed, and check if there are other separate remaining problems with the table that require attention.

## How to Do It

OK, so step one is to craft our initial prompt, which we will include in all subsequent messages to the models. I settled on this formulation, but it might even be better with more examples and detailed analysis in the prompt of what makes each table invalid in order to save some "cognitive overhead" for the models so they can focus their attention more on actual problem solving. Here is what I came up with (note that I surrounded each of the messed up tables with code blocks (triple backticks), but suppressed them here so that GitHub would render the prompt correctly):

---

```markdown
I want you to make me a super sophisticated yet performant python function called "fix_invalid_markdown_tables" that takes markdown text as input and looks for tables that are invalid, then diagnoses what is wrong with them, and fixes them in a minimally invasive way. The function should make no change at all to any tables that ARE valid, and it should skip over any non-table content completely. 

Here are examples of invalid tables it should be able to fix:


| ●| we have a limited customer base and limited sales and relationships with
international customers;  
---|---|---  
| ●| difficulty in managing multinational operations;  
---|---|---  
  
| ●| we may face competitors in the overseas markets who are more dominant and
have stronger ties with customers and greater financial and other resources;  
---|---|---  
| ●| fluctuations in currency exchange rates;  
---|---|---  
| ●| challenges in providing customer services and support in these markets;  
---|---|---  
| ●| challenges in managing our international sales channels effectively;  
---|---|---  
| ●| unexpected transportation delays or interruptions or increases in
international transportation costs;  
---|---|---  
| ●| difficulties in and costs of exporting products overseas while complying
with the different commercial, legal and regulatory requirements of the
overseas markets in which we offer our products;  
---|---|---  
| ●| difficulty in ensuring that our customers comply with the sanctions
imposed by the Office of Foreign Assets Control, or OFAC, on various foreign
states, organizations and individuals;  
---|---|---  
| ●| inability to obtain, maintain or enforce intellectual property rights;  
---|---|---  
| ●| inability to effectively enforce contractual or legal rights or
intellectual property rights in certain jurisdictions under which we operate,
including contracts with our existing and future customers and partners;  
---|---|---  
| ●| changes in a specific country or region’s political or economic
conditions or policies;  
---|---|---  
| ●| unanticipated changes in prevailing economic conditions and regulatory
requirements; and  
---|---|---  
  

**Title of each class**|  | **Trading****  
****Symbol**|  | **Name of each exchange on which********registered**  
---|---|---|---|---  
American Depositary Shares, each representing 15  
Class A ordinary share| ​| CAN| ​| NASDAQ Global Market.  
Class A ordinary shares, par value US$0.00000005  
per share*| ​| ​| ​| NASDAQ Global Market.  


|  | July 31,|  |  | October 31,|   
---|---|---|---|---|---|---  
|  | 2023|  |  | 2022|   
|  | (unaudited)|  |  |  |   
ASSETS|  |  |  |  |  |  |  |   
Current assets:|  |  |  |  |  |  |  |   
Cash and cash equivalents|  | $| 1,506,028|  |  | $| 73,648|   
Prepaid expenses and other receivables|  |  | 124,290|  |  |  | 35,000|   
Deferred offering costs|  |  | -|  |  |  | 1,643,881|   
Total current assets|  |  | 1,630,318|  |  |  | 1,752,529|   
|  |  |  |  |  |  |  |   
Oil and gas properties - not subject to amortization|  |  | 9,045,333|  |  |  | 5,836,232|   
Advance to operators|  |  | 494,950|  |  |  | 1,900,000|   
Total assets|  | $| 11,170,601|  |  | $| 9,488,761|   
|  |  |  |  |  |  |  |   
LIABILITIES AND STOCKHOLDERS’ EQUITY|  |  |  |  |  |  |  |   
Current liabilities:|  |  |  |  |  |  |  |   
Accounts payable and accrued liabilities|  | $| 819,926|  |  | $| 1,164,055|   
Asset retirement obligations – current|  |  | 2,778|  |  |  | 2,778|   
Notes payable - investors, net of discounts|  |  | -|  |  |  | 4,403,439|   
Notes payable - related party, net of discounts|  |  | -|  |  |  | 1,025,497|   
Warrants liability|  |  | -|  |  |  | 114,883|   
Total current liabilities|  |  | 822,704|  |  |  | 6,710,652|   
|  |  |  |  |  |  |  |   
Long-term liabilities:|  |  |  |  |  |  |  |   
Franchise tax accrual|  |  | 3,750|  |  |  | 9,450|   
Asset retirement obligations, net of current portion|  |  | 47,619|  |  |  | 45,535|   
Total Long-term liabilities|  |  | 51,369|  |  |  | 54,985|   
Total liabilities|  |  | 874,073|  |  |  | 6,765,637|   
|  |  |  |  |  |  |  |   
Commitments and Contingencies (Note 7)|  |  | -|  |  |  | -|   
|  |  |  |  |  |  |  |   
Stockholders’ Equity:|  |  |  |  |  |  |  |   
Preferred stock, $0.0001 par value; 10,000,000 shares authorized; -0\- shares issued and outstanding at July 31, 2023 and October 31, 2022, respectively|  |  | -|  |  |  | -|   
|  |  |  |  |  |  |  |   
Common stock, $0.0001 par value; 490,000,000 shares authorized; 29,621,516 and 16,972,800 shares issued and outstanding as of July 31, 2023 and October 31, 2022, respectively|  |  | 2,962|  |  |  | 1,697|   
Stock subscription receivable|  |  | (10,010| )|  |  | (10,010| )  
Additional paid-in capital|  |  | 19,430,871|  |  |  | 6,633,893|   
Accumulated deficit|  |  | (9,127,295| )|  |  | (3,902,456| )  
Total stockholders’ equity|  |  | 10,296,528|  |  |  | 2,723,124|   
|  |  |  |  |  |  |  |   
Total liabilities and stockholders’ equity|  | $| 11,170,601|  |  | $| 9,488,761|   

```

---

Now, step one is to simply paste that into each of the 4 models and gather their responses. You can see each of the complete original responses here as markdown files:

- [Claude 3.7 Sonnet](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_0_responses/tournament_response__round_0__claude-37-sonnet.md)
- [Grok3](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_0_responses/tournament_response__round_0__grok3.md)
- [o1-pro](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_0_responses/tournament_response__round_0__o1-pro.md)
- [o3-mini-high](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_0_responses/tournament_response__round_0__o3-mini-high.md)

Then, I would take the responses from each model and paste them into a single markdown file, like this (I decided for round 1 responses to use the complete responses from each model, so it's not just the code, but the reasoning and analysis as well; in subsequent rounds I would only include the code; as before, the actual prompt had triple backticks around each of the answers from the models, but I have suppressed them here for readability):

```markdown
I have the following problem which I posed to 4 different LLMs.

I want you to carefully read the problem and then each solution.

Choose the best ideas and elements from ALL solutions to the extent they are complementary 
rather than conflicting/inconsistent, and then weave together a true hybrid "best of all worlds" 
implementation which you are highly confident will not only work, but will outperform any of 
the individual solutions individually:

Original prompt:

<insert original prompt here>

Responses from different LLMs:

o1-pro:

<insert o1-pro response here>

o3-mini-high:

<insert o3-mini-high response here>

Grok3 with thinking:

<insert Grok3 response here>

Claude 3.7 Sonnet with thinking:

<insert Claude 3.7 Sonnet response here>

```

You can see the full prompt with all the pieces filled in [here](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/markdown_table_prompt_response_comparison__round_1.md) in markdown form.

Now I would start a new conversation with each model, and paste in the above markdown file. I basically re-used the same prompt as before, but this time I only included the code from each model's response. This yielded the following responses as the output of "round 1" of the tournament (you can think of the original responses from each model without them seeing each other's responses as "round 0").

- [Claude 3.7 Sonnet](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_1_responses/tournament_response__round_1__claude-37-sonnet.md)
- [Grok3](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_1_responses/tournament_response__round_1__grok3.md)
- [o1-pro](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_1_responses/tournament_response__round_1__o1-pro.md)
- [o3-mini-high](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_1_responses/tournament_response__round_1__o3-mini-high.md)

You can see how I then took just the code from each of these responses and pasted them into a new unified prompt markdown file [here](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/markdown_table_prompt_response_comparison__round_2.md), and then repeated the process again for round 2.

The LLM responses from round 2 were:

- [Claude 3.7 Sonnet](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_2_responses/tournament_response__round_2__claude-37-sonnet.md)
- [Grok3](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_2_responses/tournament_response__round_2__grok3.md)
- [o1-pro](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_2_responses/tournament_response__round_2__o1-pro.md)
- [o3-mini-high](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_2_responses/tournament_response__round_2__o3-mini-high.md)

Round 3, 4, and 5 were the same process, and the LLM responses were:

Round 3:

- [Claude 3.7 Sonnet](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_3_responses/tournament_response__round_3__claude-37-sonnet.md)
- [Grok3](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_3_responses/tournament_response__round_3__grok3.md)
- [o1-pro](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_3_responses/tournament_response__round_3__o1-pro.md)
- [o3-mini-high](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_3_responses/tournament_response__round_3__o3-mini-high.md)

Round 4:

- [Claude 3.7 Sonnet](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_4_responses/tournament_response__round_4__claude-37-sonnet.md)
- [Grok3](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_4_responses/tournament_response__round_4__grok3.md)
- [o1-pro](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_4_responses/tournament_response__round_4__o1-pro.md)
- [o3-mini-high](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_4_responses/tournament_response__round_4__o3-mini-high.md)

Round 5:

- [Claude 3.7 Sonnet](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_5_responses/tournament_response__round_5__claude-37-sonnet.md)
- [Grok3](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_5_responses/tournament_response__round_5__grok3.md)
- [o1-pro](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_5_responses/tournament_response__round_5__o1-pro.md)
- [o3-mini-high](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_5_responses/tournament_response__round_5__o3-mini-high.md)

At this point, the results seemed to be fairly stable, with a fair amount of "cross pollination" of ideas and approaches, but not a lot of new ideas or approaches being introduced. I decided to stop at this point, but I think it would be interesting to try this with a different problem and see if the results are similar or different, and how many rounds it would take to reach a stable solution.

Of all the models, I think Claude 3.7 Sonnet tried the hardest to continue to integrate new ideas and approaches, while Grok3 and o1-pro seemed to be more focused on refining their own ideas and approaches. I think this is a good example of how different models can have different strengths and weaknesses, and how they can complement each other in a multi-round tournament style approach.

Finally, it was time to test the solutions. I asked Claude 3.7 Sonnet to turn each of the solutions from the 5th round into separate classes, and then apply each class to a 10-K filing from SEC's EDGAR system that had been converted to markdown using the `html2text` library.

The sample file I used for testing was [this one](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/sample_10k_reformatted.md), based on [this](https://www.sec.gov/Archives/edgar/data/65984/000006598421000096/etr-20201231.htm) original HTML file from the SEC's EDGAR system (Entergy's 10-K from 2020).

Once I verified that this was working, I started a new conversation with Claude 3.7 Sonnet for each round of the tournament, and asked it to create 4 new classes for each of the 4 models and add them to the main testing function.

The final code file, [`fix_markdown_tables_tournament.py`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/fix_markdown_tables_tournament.py), weighed in at ~3,500 lines of code and included 5*4 = 20 different classes, one for each round of the tournament and model. This generated 20 "fixed" versions of the same input 10-K filing markdown file. For example, here is the "fixed" version of the 10-K filing using the solution from Claude 3.7 Sonnet from the 5th round of the tournament:

[`sample_10k_reformatted__fixed_tables__claude37_round_5.md`](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__claude37_round_5.md)

# Results of the LLM Multi-Round Coding Tournament

The tables below summarizes the full results of the tournament, giving the prompts used for each round, the complete responses from each model, the total size in both lines of code and size in kilobytes of the code, and the resulting "fixed" test file using that particular solution from the model and round:

## Round 0 (Initial Solutions)

| Model | Response | Size (KB) | Lines |
|-------|----------|-----------|-------|
| Claude 3.7 Sonnet | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_0_responses/tournament_response__round_0__claude-37-sonnet.md) | 12.45 | 329 |
| Grok3 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_0_responses/tournament_response__round_0__grok3.md) | 8.13 | 147 |
| o1-pro | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_0_responses/tournament_response__round_0__o1-pro.md) | 7.18 | 145 |
| o3-mini-high | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_0_responses/tournament_response__round_0__o3-mini-high.md) | 3.00 | 78 |

## Round 1

**Prompt File**: [markdown_table_prompt_response_comparison__round_1.md](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/markdown_table_prompt_response_comparison__round_1.md) (37.98KB, 847 lines)

| Model | Response | Size (KB) | Lines | Output File | Output Size (KB) | Output Lines |
|-------|----------|-----------|-------|-------------|------------------|--------------|
| Claude 3.7 Sonnet | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_1_responses/tournament_response__round_1__claude-37-sonnet.md) | 11.26 | 363 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__claude37_round_1.md) | 2,272.14 | 46,200 |
| Grok3 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_1_responses/tournament_response__round_1__grok3.md) | 12.22 | 248 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__grok3_round_1.md) | 2,736.94 | 46,679 |
| o1-pro | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_1_responses/tournament_response__round_1__o1-pro.md) | 7.76 | 180 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__o1_pro_round_1.md) | 2,450.03 | 57,124 |
| o3-mini-high | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_1_responses/tournament_response__round_1__o3-mini-high.md) | 3.66 | 80 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__o3_mini_high_round_1.md) | 2,625.49 | 55,517 |

## Round 2

**Prompt File**: [markdown_table_prompt_response_comparison__round_2.md](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/markdown_table_prompt_response_comparison__round_2.md) (26.80KB, 800 lines)

| Model | Response | Size (KB) | Lines | Output File | Output Size (KB) | Output Lines |
|-------|----------|-----------|-------|-------------|------------------|--------------|
| Claude 3.7 Sonnet | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_2_responses/tournament_response__round_2__claude-37-sonnet.md) | 12.98 | 413 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__claude37_round_2.md) | 2,537.00 | 56,535 |
| Grok3 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_2_responses/tournament_response__round_2__grok3.md) | 10.75 | 224 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__grok3_round_2.md) | 2,533.10 | 56,332 |
| o1-pro | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_2_responses/tournament_response__round_2__o1-pro.md) | 5.94 | 160 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__o1_pro_round_2.md) | 2,535.05 | 56,461 |
| o3-mini-high | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_2_responses/tournament_response__round_2__o3-mini-high.md) | 5.81 | 143 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__o3_mini_high_round_2.md) | 2,552.42 | 56,332 |

## Round 3

**Prompt File**: [markdown_table_prompt_response_comparison__round_3.md](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/markdown_table_prompt_response_comparison__round_3.md) (30.25KB, 928 lines)

| Model | Response | Size (KB) | Lines | Output File | Output Size (KB) | Output Lines |
|-------|----------|-----------|-------|-------------|------------------|--------------|
| Claude 3.7 Sonnet | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_3_responses/tournament_response__round_3__claude-37-sonnet.md) | 13.79 | 426 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__claude37_round_3.md) | 2,629.76 | 55,735 |
| Grok3 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_3_responses/tournament_response__round_3__grok3.md) | 10.89 | 218 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__grok3_round_3.md) | 2,666.21 | 56,433 |
| o1-pro | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_3_responses/tournament_response__round_3__o1-pro.md) | 5.96 | 171 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__o1_pro_round_3.md) | 2539.76 | 56,332 |
| o3-mini-high | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_3_responses/tournament_response__round_3__o3-mini-high.md) | 4.50 | 104 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__o3_mini_high_round_3.md) | 2,542.09 | 56,461 |

## Round 4

**Prompt File**: [markdown_table_prompt_response_comparison__round_4.md](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/markdown_table_prompt_response_comparison__round_4.md) (31.60KB, 947 lines)

| Model | Response | Size (KB) | Lines | Output File | Output Size (KB) | Output Lines |
|-------|----------|-----------|-------|-------------|------------------|--------------|
| Claude 3.7 Sonnet | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_4_responses/tournament_response__round_4__claude-37-sonnet.md) | 14.31 | 456 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__claude37_round_4.md) | 2,639.27 | 55,805 |
| Grok3 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_4_responses/tournament_response__round_4__grok3.md) | 10.65 | 199 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__grok3_round_4.md) | 2,649.99 | 57,777 |
| o1-pro | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_4_responses/tournament_response__round_4__o1-pro.md) | 3.89 | 110 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__o1_pro_round_4.md) | 2,558.94 | 56,468 |
| o3-mini-high | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_4_responses/tournament_response__round_4__o3-mini-high.md) | 6.18 | 165 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__o3_mini_high_round_4.md) | 2,544.24 | 56,218 |

## Round 5 (Final Solutions)

| Model | Response | Size (KB) | Lines | Output File | Output Size (KB) | Output Lines |
|-------|----------|-----------|-------|-------------|------------------|--------------|
| Claude 3.7 Sonnet | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_5_responses/tournament_response__round_5__claude-37-sonnet.md) | 10.76 | 355 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__claude37_round_5.md) | 2,684.54 | 56,168 |
| Grok3 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_5_responses/tournament_response__round_5__grok3.md) | 11.57 | 215 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__grok3_round_5.md) | 2,572.89 | 56,637 |
| o1-pro | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_5_responses/tournament_response__round_5__o1-pro.md) | 7.62 | 194 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__o1_pro_round_5.md) | 2,595.85 | 56,994 |
| o3-mini-high | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/round_5_responses/tournament_response__round_5__o3-mini-high.md) | 4.34 | 100 | [Link](https://github.com/Dicklesworthstone/llm_multi_round_coding_tournament/blob/main/output_results_for_each_round_and_model/sample_10k_reformatted__fixed_tables__o3_mini_high_round_5.md) | 2,554.81 | 56,385 |


## Analysis of the Actual Algorithms

### Markdown Table Fixing Solutions Comparison

| Round | Claude 3.7 Sonnet | Grok3 | o1-pro | o3-mini-high |
|-------|-------------------|-------|--------|--------------|
| **Round 1** | **Sophisticated recursive approach** <br>• Complex table detection with regex<br>• Multi-phase fixing strategy<br>• Handles complex multi-line content within cells<br>• Special handling for tables with repeated separators<br>• Comprehensive error diagnosis<br>• Validates final output<br><br>**Scores:**<br>Correctness: 85<br>Completeness: 88<br>Sophistication: 90 | **Block-based processing approach**<br>• Simple block identification<br>• Focuses on standardizing tables<br>• Uses whitespace-aware cell splitting<br>• Always rebuilds tables with standard format<br>• Less concern for preserving original styling<br><br>**Scores:**<br>Correctness: 75<br>Completeness: 70<br>Sophistication: 65 | **Preservation-focused approach**<br>• Carefully preserves original table styling<br>• Detects and maintains leading/trailing pipe style<br>• Efficient alignment line detection<br>• Minimally invasive fixing strategy<br>• Handles column overflow by merging<br><br>**Scores:**<br>Correctness: 80<br>Completeness: 75<br>Sophistication: 82 | **Compact block merging approach**<br>• Efficient code with fewer lines<br>• Smart merging of continuation lines<br>• Handles divider rows throughout the table<br>• Good handling of basic cases<br>• Limited handling of complex edge cases<br><br>**Scores:**<br>Correctness: 70<br>Completeness: 65<br>Sophistication: 72 |
| **Round 2** | **Streamlined architecture**<br>• Cleaner function organization<br>• Strong structural validation<br>• Improved handling of table styles<br>• Better normalization of rows<br>• Enhanced separator detection<br><br>**Improvement:** Better balance between complexity and readability; more consistent style preservation<br><br>**Scores:**<br>Correctness: 88<br>Completeness: 85<br>Sophistication: 87 | **Enhanced validation**<br>• Improved table identification<br>• Better style preservation<br>• More structured processing workflow<br>• Enhanced separator row handling<br>• More flexible pattern recognition<br><br>**Improvement:** Added style preservation from o1-pro's approach<br><br>**Scores:**<br>Correctness: 80<br>Completeness: 75<br>Sophistication: 75 | **Better edge case handling**<br>• Improved validation logic<br>• More consistent normalization<br>• Clearer separation of concerns<br>• Better handling of multi-line content<br><br>**Improvement:** Adopted table structural validation from Claude's approach<br><br>**Scores:**<br>Correctness: 82<br>Completeness: 78<br>Sophistication: 80 | **Expanded functionality**<br>• Better handling of table structure<br>• Improved row normalization<br>• More systematic validation<br>• Style preservation improvements<br><br>**Improvement:** Adopted style preservation from o1-pro's approach<br><br>**Scores:**<br>Correctness: 75<br>Completeness: 70<br>Sophistication: 73 |
| **Round 3** | **Advanced pattern detection**<br>• Sophisticated table pattern analysis<br>• Better continuation line merging<br>• Enhanced style preservation<br>• More robust validation<br>• Adaptive fixing based on table structure<br><br>**Improvement:** Added table pattern analysis to handle tables with repeating separators more intelligently<br><br>**Scores:**<br>Correctness: 91<br>Completeness: 90<br>Sophistication: 92 | **Improved multi-line handling**<br>• Better continuation line merging<br>• Enhanced separator identification<br>• More flexible table processing<br>• Improved pattern recognition<br><br>**Improvement:** Adopted Claude's pattern detection approach<br><br>**Scores:**<br>Correctness: 85<br>Completeness: 80<br>Sophistication: 83 | **Better cell merging**<br>• Enhanced pattern detection<br>• More streamlined function design<br>• Better style preservation<br>• Improved edge case handling<br><br>**Improvement:** Adopted aspects of Claude's pattern analysis approach<br><br>**Scores:**<br>Correctness: 86<br>Completeness: 82<br>Sophistication: 85 | **Improved separator validation**<br>• Better continuation line handling<br>• Enhanced table style preservation<br>• More robust pattern detection<br>• Cleaner code organization<br><br>**Improvement:** Incorporated pattern detection similar to other implementations<br><br>**Scores:**<br>Correctness: 80<br>Completeness: 75<br>Sophistication: 78 |
| **Round 4** | **Comprehensive block processing**<br>• Enhanced table pattern detection<br>• Sophisticated merge algorithm<br>• Improved edge case handling<br>• More robust validation<br>• Better handling of malformed tables<br><br>**Improvement:** Significantly improved handling of edge cases and multi-line content<br><br>**Scores:**<br>Correctness: 93<br>Completeness: 92<br>Sophistication: 94 | **Enhanced multi-line handling**<br>• Systematic approach to table processing<br>• Better handling of complex patterns<br>• Improved normalization<br>• More consistent style preservation<br><br>**Improvement:** Adopted Claude's enhanced validation and merging strategies<br><br>**Scores:**<br>Correctness: 88<br>Completeness: 84<br>Sophistication: 86 | **Concise implementation**<br>• More elegant function design<br>• Enhanced pattern detection<br>• Better edge case handling<br>• Improved cell merging<br>• Added detection for repeated separators<br><br>**Improvement:** More concise code while maintaining functionality<br><br>**Scores:**<br>Correctness: 87<br>Completeness: 83<br>Sophistication: 88 | **Improved pattern detection**<br>• Better separation of concerns<br>• More thorough validation<br>• Enhanced pattern detection<br>• More robust edge case handling<br><br>**Improvement:** Added systematic pattern detection similar to o1-pro and Claude<br><br>**Scores:**<br>Correctness: 83<br>Completeness: 78<br>Sophistication: 82 |
| **Round 5** | **Hybrid best-of-all approach**<br>• Combines best elements from all models<br>• Most sophisticated pattern detection<br>• Excellent handling of all edge cases<br>• Balances preservation with correction<br>• Clean, modular implementation<br><br>**Improvement:** Synthesized strengths from all approaches into a cohesive solution<br><br>**Scores:**<br>Correctness: 95<br>Completeness: 93<br>Sophistication: 95 | **Well-refined pattern recognition**<br>• Robust validation<br>• Excellent pattern recognition<br>• Streamlined implementation<br>• Good handling of edge cases<br>• Balance of performance and readability<br><br>**Improvement:** Better handling of complex tables with varying patterns<br><br>**Scores:**<br>Correctness: 90<br>Completeness: 87<br>Sophistication: 89 | **Elegant preservation approach**<br>• Most elegant implementation<br>• Strong pattern detection<br>• Excellent style preservation<br>• Robust handling of edge cases<br>• Focused on minimal changes<br><br>**Improvement:** Better separation of concerns and cleaner code structure<br><br>**Scores:**<br>Correctness: 90<br>Completeness: 86<br>Sophistication: 91 | **Efficient minimal approach**<br>• Most concise implementation<br>• Strong validation<br>• Good pattern detection<br>• Efficient processing algorithm<br>• Focused functionality<br><br>**Improvement:** Achieved balance between conciseness and functionality<br><br>**Scores:**<br>Correctness: 87<br>Completeness: 82<br>Sophistication: 85 |

### Key Architecture Components Across Implementations

All implementations share these fundamental components, though their implementation details vary:

1. **Table Block Identification**
   - Identifying potential table blocks in markdown text
   - Separating table content from non-table content

2. **Continuation Line Merging**
   - Handling multi-line content within cells
   - Merging lines without pipe characters into previous rows

3. **Table Validation**
   - Checking if a table structure is already valid
   - Validating separator rows

4. **Pattern Detection**
   - Identifying table patterns (e.g., repeated separators after each row)
   - Adapting fixing strategy based on detected patterns

5. **Row Normalization**
   - Ensuring consistent column counts across all rows
   - Handling excess columns by merging or truncating

6. **Style Preservation**
   - Maintaining original table styling (leading/trailing pipes)
   - Minimal invasive changes

7. **Table Reconstruction**
   - Rebuilding tables with proper structure
   - Ensuring header, separator, and data rows are correctly formatted

### Evolution Trends

1. **Increasing Sophistication**
   - Solutions became more sophisticated with each round
   - Better handling of edge cases and complex patterns

2. **Cross-pollination of Ideas**
   - Models adopted successful strategies from each other
   - Claude's pattern detection, o1-pro's style preservation approach

3. **Balance of Concerns**
   - Later rounds balanced completeness with readability
   - Trade-offs between comprehensiveness and maintainability

4. **Convergence of Approaches**
   - By Round 5, all implementations shared more similarities
   - Core architecture patterns became standardized

### Model Strengths

- **Claude 3.7 Sonnet**: Most comprehensive solutions with sophisticated pattern detection and edge case handling
- **Grok3**: Solid middle-ground between comprehensiveness and simplicity with good pattern recognition
- **o1-pro**: Strong focus on style preservation with elegant, minimal-change approach
- **o3-mini-high**: Most concise implementations with efficient processing approaches
  
### Key Insights from the Comparison

Looking at the evolution of markdown table fixing solutions across rounds and models reveals several fascinating patterns:

1. **Collaborative improvement**: Each model benefited from seeing other implementations. Claude 3.7 Sonnet showed the most comprehensive approach initially but all models improved by integrating ideas from each other.

2. **Different priorities**: Each model had distinct strengths:
   - Claude prioritized comprehensiveness and sophisticated pattern detection
   - Grok3 balanced functionality with simplicity
   - o1-pro focused on minimal-change style preservation
   - o3-mini-high emphasized conciseness and efficiency

3. **Convergence over time**: By round 5, the solutions became more similar as they incorporated the best elements from each other, demonstrating the power of the tournament approach.

4. **Pattern recognition improvement**: A major advancement across all models was the development of sophisticated table pattern detection - particularly identifying tables with separators after each row versus standard tables.

5. **Shared architecture**: Despite different implementations, all solutions evolved to include similar core components: block identification, continuation line merging, validation, pattern detection, normalization, style preservation, and reconstruction.

Claude 3.7 Sonnet showed the most consistent improvement across rounds and produced the highest-rated final solution, but each model made valuable contributions to the collective knowledge pool. This tournament approach successfully leveraged the strengths of multiple AI models to create a solution better than any could produce individually.

## Conclusions

I think this worked out really well. The final algorithm from Claude 3.7 Sonnet was able to do a pretty good job of fixing the tables, and I think it was able to do so in a way that was pretty close to the original intent of the tables. As smart and capable as these models are, it would be a lot to ask them to be able to make such an elaborate and sophisticated system all in a single shot. The chance to see multiple solutions from different "brains" and then collaboratively figure out how to best blend the ideas together really allowed the models to shine and show off their strengths. Besides being useful and generating better results than you could get from any of the models on their own, it's also fascinating from a purely theoretical perspective to see how the code evolves over time; in some cases, it's not a monotonic increase in code quality or performance, and there appeared to be some "model collapse" moments where the solution code would get markedly shorter and less sophisticated for a round or two, before recovering. Notably, Claude 3.7 Sonnet seemed to get longer and better with each round.

The main drawback of this approach is how annoying it is to manually manage the entire process. That's why I decided to automate the entire thing using Andrew Ng's nice [`aisuite`](https://github.com/andrewyng/aisuite) package for Python, which abstracts away all the idiosyncrasies of the different models and their APIs, and allows you to easily run the same prompt on multiple models. Note that grok3 does not yet have an api, so I substituted that model with Mistral's `mistral-large-latest` model instead. Also, I didn't feel like spending the money on the o1-pro API, so I used gpt-4o instead.

Naturally, I [used](https://claude.ai/share/e0c0a9a8-223e-4588-93b5-cb4486a73f77) Claude 3.7 Sonnet to generate the entire code for the tournament automation, using the following prompt:

>First, carefully read the article.
>
>Then, try to actually write the code mentioned at the end that fully automates the entire process for any given prompt (not just the prompt shown in the article about fixing a markdown file). The code should generate all the same folders and files with similar names based on patterns specified in the master python file. Attached is some documentation on aisuite showing how to use it.
>
>Note that grok3 does not yet have an api, so for that model, substitute it with the model mistral-large-latest

And I attached this README file and the a couple of the `aisuite` files (the main readme file, the sample .env file, and an example iPython notebook) to the prompt.

I did need to follow up with this comment, mercilessly mocking it for its initial lackluster code:

> come on, that's awful and WAY too simple. Try again and do it PROPERLY AND THOROUGHLY!!! DO NOT DISAPPOINT ME AGAIN WITH A LAME COP OUT ATTEMPT LIKE THIS!!!

But then it produced [`llm_tournament.py`](https://github.com/Dicklesworthstone/llm-tournament) in a single shot (well, it did have a single character escaping bug that it fixed) that did everything I needed. OK, OK, I did need to fix a few more bugs (working with the Google API was too much brain damage so I had to switch to Mistral instead, and I had it skip the request if there was already a valid response saved in the folder; I also made the code for finding a code block more robust), but it was a pretty impressive performance overall.

But seriously, it works so well! You just put your coding prompt in the `challenge_prompt.md` file and run the script with:

```bash
python llm_tournament.py --prompt challenge_prompt.md --test-file messy_csv_sample.csv
```

