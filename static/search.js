/**
 * Created with PyCharm.
 * User: ehebel
 * Date: 26-02-14
 * Time: 16:01
 * To change this template use File | Settings | File Templates.
 */
function search_submit(){
    var query = $("#id_query").val();
    $("#search-results").load(
      "/modelador_light/search-form/?ajax&query=" + encodeURIComponent(query)
    );
    return false;
}

$(document).ready(function (){
   $("#search-form").submit(search_submit);
});