
package metamap;

import gov.nih.nlm.nls.metamap.*;

import java.io.InputStream;
import java.io.PrintStream;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.File;
import java.util.List;
import java.util.ArrayList;

import se.sics.prologbeans.PrologSession;

import java.util.Vector;
import java.util.Set;
import java.util.HashSet;

import LvgNormApi.Norm;

//import metamap.util.Cartesian;

// class used to perform cui lookup with metamap api
public class MetaMap {

    MetaMapApi api;
    Norm normalizer;

    public MetaMap() {
        this(MetaMapApi.DEFAULT_SERVER_HOST, MetaMapApi.DEFAULT_SERVER_PORT);
    }

    // set options
    public MetaMap(String serverHostName, int serverPort)
    {

        this.api = new MetaMapApiImpl();
        this.api.setHost(serverHostName);
        this.api.setPort(serverPort);
        this.api.setOptions("--show_cuis -z -i -a -g" );

        try {
            normalizer = new Norm();
        }
        catch (Exception e)
        {
            System.out.println(e.getMessage());
        }

   }

    private Vector<String> normalizeTerm(String term) {

        Vector<String> result = null;

        Vector<String> out = normalizer.normalize(term);

        if (out.size() > 0) {
            result = out;
        }
        else {
            result = new Vector<String>();
            result.add(term);
        }

        return result;

    }

    public Set<String> generateTerms(String term) {

        Set<String> terms = new HashSet<>();

        String strippedTerm = term.replaceAll("[^a-zA-Z0-9 ]*", "");

        /*
        String[] tokens = term.split("\\s+");

        Vector<Vector<String>> normTokens = new Vector<Vector<String>>();

        for (String t : tokens) {
            normTokens.add(normalizeTerm(t));
        }

        for (String phrase : Cartesian.setsOfTokensToStrings(normTokens)) {
            terms.add(phrase);
        }
        */

        terms.add(term);

        terms.add(strippedTerm);

        terms.addAll(normalizeTerm(term));
        if (term.equals(strippedTerm) == false) {
            terms.addAll(normalizeTerm(strippedTerm));
        }


        return terms;

    }

    // print results of lookup to stdout
    public String getCuis(String arg) throws Exception
    {

//        System.out.println("called getCuis()");

//        System.out.println("term: " + arg);

        Set<String> terms = generateTerms(arg);

//        System.out.println("got terms!");

        Vector<String> results = new Vector<>();

        for (String term : terms) {

            // get result
            List<Result> resultList = this.api.processCitationsFromString(term);

            // iterate over results
            for (Result result: resultList) {

                if (result.getUtteranceList().size() == 0) {
                    results.add("NORM|" + term + "|STR|" + term + "|CUI|" + "CUI-less");
                    break;
                }

                for (Utterance utterance: result.getUtteranceList()) {
                    for (PCM pcm: utterance.getPCMList()) {

                        if ( pcm.getMappingList().size() < 1 ) {
                            results.add("NORM|" + term + "|STR|" + term + "|CUI|" + "CUI-less");
                            break;
                        }

                        String output = new String("");

                        for (Mapping map: pcm.getMappingList()) {
                            for (Ev mapEv: map.getEvList()) {
                                results.add("NORM|" + term + "|STR|" + mapEv.getPreferredName() + "|CUI|" + mapEv.getConceptId());
                            }
                        }
                    }
                }
            }
        }
        return formatResults(results);
    }

    public String formatResults(Vector<String> results) {

        String retStr = results.elementAt(0);

        for (int i=1; i<results.size();i++) {
            retStr += ("&&" + results.elementAt(i));
        }

        retStr += "\n";

        return retStr;

    }

    public static void main(String[] args) throws Exception {

        // read phrase from stdin to lookup
        MetaMap api = new MetaMap(MetaMapApi.DEFAULT_SERVER_HOST, MetaMapApi.DEFAULT_SERVER_PORT);

        for (String term : api.generateTerms(args[0])) {
            System.out.println(term);
            System.out.println(api.getCuis(term));
        }

    }
}

// EOF

