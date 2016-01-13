
package parser;

import java.util.Collection;
import java.util.List;
import java.io.*;
import java.util.ArrayList;

import edu.stanford.nlp.process.Tokenizer;
import edu.stanford.nlp.process.TokenizerFactory;
import edu.stanford.nlp.process.CoreLabelTokenFactory;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.process.PTBTokenizer;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.Sentence;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.pipeline.*;
import java.util.Properties;
import edu.stanford.nlp.util.CoreMap;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.trees.CollinsHeadFinder;


public class DependencyParser {

    String parserModel;
    LexicalizedParser lp;

    TokenizerFactory<CoreLabel> tokenizerFactory;
    Properties props;

    StanfordCoreNLP pipeline;

    public DependencyParser() {

//        System.out.println("constructor called");
        parserModel = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz";
        lp = LexicalizedParser.loadModel(parserModel);

        props = new Properties();
        tokenizerFactory = PTBTokenizer.factory(new CoreLabelTokenFactory(), "");

        props.put("annotators", "tokenize, ssplit, parse");
        pipeline = new StanfordCoreNLP(props);

    };

    public static void main(String[] args) throws Exception {
        DependencyParser p = new DependencyParser();
        System.out.println(p.getDependencyTree(new String("This is a test sentence.")));

        System.out.println(p.getNounPhraseHeads(new String("This is a test sentence")));

    }

    public Tree getSentenceStructure(String sentence) {
        Annotation document = new Annotation(sentence);
        pipeline.annotate(document);

        CoreMap sent = document.get(CoreAnnotations.SentencesAnnotation.class).get(0);

        Tree parse = sent.get(TreeCoreAnnotations.TreeAnnotation.class);

//         Tree parse = document.get(TreeCoreAnnotations.TreeAnnotation.class).get(0);

        System.out.println(parse == null);

//        System.out.println(parse.toString());

        return parse;

    }

    public List<String> getNounPhraseHeads(String sentence) {

        Tree node = getSentenceStructure(sentence);

        List<String> Heads = new ArrayList<String>();

        _getNounPhraseHeads(node, null, new CollinsHeadFinder(), Heads);

//        for (String head : Heads) {

//            System.out.println(head);

//        }

        return Heads;

    }

    public void _getNounPhraseHeads(Tree node, Tree parent, HeadFinder headFinder, List<String> Heads) {

          if (node == null || node.isLeaf()) {
             return;
          }

          //if node is a NP - Get the terminal nodes to get the words in the NP
          if(node.value().equals("NP") ) {

             List<Tree> leaves = node.getLeaves();

            Heads.add(node.headTerminal(headFinder, parent).toString());

        }

        for(Tree child : node.children()) {
             _getNounPhraseHeads(child, node, headFinder, Heads);
        }

     }

    public String getDependencyTree(String sentence)  {

        /* Process all tokens within the tokens data member then clear the list.
           this is done because I could not figure out how to pass objects in py4j */

        Tokenizer<CoreLabel> tok = tokenizerFactory.getTokenizer(new StringReader(sentence));
        List<CoreLabel> rawWords = tok.tokenize();

        Tree parse = lp.apply(rawWords);
        TreebankLanguagePack tlp = lp.treebankLanguagePack(); // PennTreebankLanguagePack for English
        GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
        GrammaticalStructure gs = gsf.newGrammaticalStructure(parse);

        Annotation document = new Annotation(sentence);
        pipeline.annotate(document);

        return gs.dependenciesToCoNLLXString(gs, document);

    }


}

// EOF

