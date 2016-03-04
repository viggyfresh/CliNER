
/*
 * This is a class is used so cliner can access java objects using python.
 */

package gateway;

//import metamap.MetaMap;
import parser.DependencyParser;
//import opennlp.tokenizer.OpenNLPTokenizer;
import py4j.GatewayServer;

class EntryPoint {

//    MetaMap metaMapApi;
    DependencyParser stanfordParser;
    //OpenNLPTokenizer openNlpTokenizer;

    public EntryPoint() {
        try {
  //          metaMapApi = new MetaMap();
            stanfordParser = new DependencyParser();
      //      openNlpTokenizer = new OpenNLPTokenizer();
        }
        catch(Exception e){
            System.out.println(e.getMessage());
        }
    }

    //public MetaMap getMetaMapObj() {

      //  return metaMapApi;

  //  }

    public DependencyParser getStanfordParserObj() {

        return stanfordParser;

    }

    /*
    public OpenNLPTokenizer getOpenNlpTokenizer() {
        return openNlpTokenizer;
    }
    */

    public static void main(String[] args) {
        EntryPoint ep = new EntryPoint();

        try {

            //ep.getMetaMapObj().getCuis("test");

            //System.out.println(ep.getStanfordParserObj().getDependencyTree("this is a test sentence"));

            //ep.getOpenNlpTokenizer().preProcess("This is a test sentence");

        }
        catch (Exception e) {

            System.out.println(e.getMessage());

        }

    }

}


