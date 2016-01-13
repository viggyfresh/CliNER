
package opennlp.tokenizer;

import opennlp.tools.sentdetect.SentenceModel;
import opennlp.tools.sentdetect.SentenceDetectorME;
import opennlp.tools.tokenize.TokenizerModel;
import opennlp.tools.tokenize.TokenizerME;
import java.io.InputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Vector;
import java.util.List;
import java.util.ArrayList;


public class OpenNLPTokenizer {

    private SentenceModel sent_model;
    private TokenizerModel tok_model;
    private SentenceDetectorME sentenceDetector;
    private TokenizerME tokenDetector;

    public OpenNLPTokenizer() throws Exception {

        String modelPath = new String(System.getenv("CLINER_DIR"));
        modelPath += "/clicon/lib/java/openNLP/models";

        InputStream sentModelIn = new FileInputStream(modelPath + "/en-sent.bin");
        InputStream tokModelIn = new FileInputStream(modelPath + "/en-token.bin");

        try {
            this.sent_model = new SentenceModel(sentModelIn);
            this.tok_model  = new TokenizerModel(tokModelIn);
        }
        catch (IOException e) {
          e.printStackTrace();
        }
        finally {
          if (sentModelIn != null) {
            try {
              sentModelIn.close();
            }
            catch (IOException e) {
            }
          }
          if (tokModelIn != null) {
            try {
              tokModelIn.close();
            }
            catch (IOException e) {
            }
          }

        }
        this.sentenceDetector = new SentenceDetectorME(sent_model);
        this.tokenDetector    = new TokenizerME(tok_model);

    }

    public List<String[]> preProcess(String text) {

        String[] sentences = this.sentenize(text);

        List<String[]> retval = new ArrayList<String[]>();

        for(String sentence : sentences) {
            retval.add(tokenize(sentence));
        }

        return retval;

    }

    public String[] sentenize(String text) {
        return this.sentenceDetector.sentDetect(text);
    }

    public String[] tokenize(String text) {
        return this.tokenDetector.tokenize(text);
    }

    public static void main(String[] args) {

        return;

    }


}


