
package metamap.util;

import java.util.Set;
import java.util.HashSet;
import java.util.Vector;

public class Cartesian {

    public static Vector<Vector<?>> cartesianProduct(Vector<?> a, Vector<?> b) {
        /*
         * Compute the cartesian product of two sets.
         */

        Vector cartesianProducts = new Vector<Vector<?>>();

        for(Object item : a) {

            for (Object item2: b) {

                Vector pair = new Vector<>();

                pair.add(item);
                pair.add(item2);

                cartesianProducts.add(pair);

                pair = null;

            }
        }

        return cartesianProducts;
    }

    /* TODO: figure out how to change this to Vector<Vector<String>>, getting errors */
   public static Vector<Vector<?>> cartesianProductOfTokens(Vector<Vector<String>> vectsOfTokens) {
        /*
         * Takes in a list of vects and then computes the cartesian product of all elements of all vects.
         */

        int numOfVects = vectsOfTokens.size();

        Vector<Vector<?>> cartProd = null;

        if (numOfVects >= 2){

            /* get init set */
            cartProd = cartesianProduct(vectsOfTokens.get(0), vectsOfTokens.get(1));

            for (int i = 2; i < numOfVects; i++) {

                Vector<Vector<?>> tmp = cartesianProduct(cartProd, vectsOfTokens.get(i));

                cartProd = new Vector<Vector<?>>();

                /* hack: each pair in cartesianProduct will be the pair (Vector, string) just update the pair as Vector.add(string) */
                for (Vector<?> pair : tmp) {

                    Vector<String> p = new Vector<String>((Vector<String>) (pair.get(0)));

                    p.add(((String) pair.get(1)));

                    cartProd.add(p);

                }

            }

        }
        else if (numOfVects == 1){
            // can't compute a product.
            cartProd = new Vector<Vector<?>>();
            cartProd.add(vectsOfTokens.get(0));
        }
        else {
        }

        return cartProd;

    }

    public static Vector<String> setsOfTokensToStrings(Vector<Vector<String>> vectsOfTokens) {
        Vector<String> strings = new Vector<String>();

        Vector<Vector<?>> products = cartesianProductOfTokens(vectsOfTokens);

        if (products != null) {

            for (Vector<?> tuple : products) {
                strings.add((String) String.join(" ", (Vector<String>)tuple));
            }

        }

        return strings;

    }

    public static void main(String[] args) {

        Vector<String> s1 = new Vector<java.lang.String>();
        Vector<String> s2 = new Vector<java.lang.String>();
        Vector<String> s3 = new Vector<java.lang.String>();

        s1.add("blood");
        s1.add("bloodied");

        s2.add("running");
        s2.add("run");

        s3.add("after");
        s3.add("afte");

        Vector<Vector<String>> ar = new Vector<Vector<String>>();

        ar.add(s1);
        ar.add(s2);
        ar.add(s3);

        for (String s : setsOfTokensToStrings(ar)) {
            System.out.println(s);
        }

        /*
        for (String s : setsOfTokensToStrings(s1)) {
            System.out.println(s);
        }
        */

    }


}


