function fillOptions(o)
{
//    alert(o)
    if (o.children.length >= 1) 
       { 
         while(o.firstChild)
             o.removeChild(o.firstChild)
       }
    
    c = o.previousElementSibling.value
    d = new Date();
    y = d.getFullYear(); //current year
   
    if (c == 'MSc. (CA)' || c == 'MBA-IT')
       {
           //for sem 1 and 2
           options = document.createElement('option')
           options.text = y-1 + '-' + ((y+1)%100);
           o.add(options,null)
           //for sem 3 and 4
           options = document.createElement('option')
           options.text = y + '-' + ((y+2)%100);
           o.add(options,null)
       }
    else
    {
        //for sem 5 and 6
        options = document.createElement('option')
        options.text = (y-2) + '-' + ((y+1)%100);
        o.add(options,null)
        //for sem 3 and 4
        options = document.createElement('option')
        options.text = (y-1) + '-' + ((y+2)%100);
        o.add(options,null)
        //for sem 1 and 2
        options = document.createElement('option')
        options.text = y + '-' + ((y+3)%100);
        o.add(options,null)
    }
    document.getElementById('submitbtn').removeAttribute('disabled');
}
