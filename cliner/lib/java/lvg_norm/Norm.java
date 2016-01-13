
package LvgNormApi;

import java.util.*;

import gov.nih.nlm.nls.lvg.Lib.*;
import gov.nih.nlm.nls.lvg.Api.*;

public class Norm
{

    String properties = null;
    NormApi api = null;

    public Norm() throws Exception
    {
        java.lang.Exception e = new java.lang.Exception("invalid lvg.properties path");

        if (System.getenv("CLINER_DIR") == null)
        {
            throw e;
        }
        else
        {

            properties = new String(System.getenv("CLINER_DIR") + "/cliner/lib/java/lvg_norm/lvg/data/config/lvg.properties");
            api = new NormApi(properties);
        }

    }

    private Vector<String> mutate(String str) throws Exception
    {
        return api.Mutate(str);
    }

    public Vector<String> normalize(String arg) {

        Vector<String> out = null;

        try
        {
            out = mutate(arg);
        }
        catch (Exception e) {  }

        return out;

    }

    public void displayNormOutput(String arg) {

        Vector<String> out = normalize(arg);

        if (out.size() == 0 || out == null) {
            System.out.println(arg);
            return;
        }

        // print out result
        for(int i = 0; i < out.size(); i++)
        {
            String temp = out.elementAt(i);
            if (i == 0) {
                System.out.print(temp);
            }
            else {
                System.out.print("|" + temp);
            }
        }
        System.out.print("\n");
    }

    public static void main(String[] args)
    {
        try{
            Norm normalizer = new Norm();
            for(String arg : args ){
                normalizer.displayNormOutput(arg);
            }
        }
        catch (Exception e)
        {
            System.err.println(e.getMessage());
        }


    }

}
// EOF

