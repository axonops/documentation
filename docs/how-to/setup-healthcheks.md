# Setup Healthcheks


<ol>

    <li>

        <div>

            <p>On the Axonops application menu, click <code>Healthchecks</code> and <strong>select</strong>
                <code>Setup</code>tab.</p>
            <div class="customform admonition ">
                <p class="pagerdutygif"><img class="testbtn" src="../../img/healthchekcssetup.png" alt="healthchekcssetup"></p>
            </div>
        </div>

    </li>
    <li>


        <h5>Add HealthCheck Services </h5>
        <ul>


            <li>
                <p> <code>Create service(s)</code> </p>
                <p> Below there few examples <code>copy</code> and <code>Paste</code> inside. and click <code>save</code>
                    <img class="testbtn" src="../../img/disk.png" alt="save"></p>

            </li>





            <div class="codehilite">
                <pre> {
   <span class="nt">"shellchecks":</span> [
    {
        <span class="nt">"name"</span> : <span class="s">"check_cassandra_statusbinary"</span>,
        <span class="nt">"shell"</span> :  <span class="s">"/bin/bash"</span>,
       <span class="nt"> "script":</span> <span class="s"> "/var/lib/cassandra_checks/check_cassandra_statusbinary.sh"</span>,
       <span class="nt"> "interval":</span> <span class="s">"5m"</span> ,
       <span class="nt"> "timeout": </span><span class="s">"1m"</span> 
    }
  ],

  <span class="nt">"httpchecks":</span> [
    {
        <span class="nt">"name"</span> : <span class="s">"cassandra"</span>,
        <span class="nt">"http"</span> :  <span class="s">"http://localhost:9042"</span>,
       <span class="nt"> "tls_skip_verify":</span> <span class="l l-Scalar l-Scalar-Plain"> true</span>,
       <span class="nt"> "method":</span> <span class="s">"GET"</span> ,
       <span class="nt"> "interval":</span> <span class="s">"10s"</span> ,
       <span class="nt"> "timeout": </span><span class="s">"1m"</span> 
    },
    {
        <span class="nt">"name"</span> : <span class="s">"cassandra"</span>,
        <span class="nt">"http"</span> :  <span class="s">"http://localhost:9916"</span>,
       <span class="nt"> "tls_skip_verify":</span> <span class="l l-Scalar l-Scalar-Plain"> true</span>,
       <span class="nt"> "method":</span> <span class="s">"GET"</span> ,
       <span class="nt"> "interval":</span> <span class="s">"10s"</span> ,
       <span class="nt"> "timeout": </span><span class="s">"1m"</span> 
    }
  ],
  <span class="nt">"tcpchecks":</span> [
    {
        <span class="nt">"name"</span> : <span class="s">"tcp_cassandra"</span>,
        <span class="nt">"tcp"</span> :  <span class="s">"http://localhost:9042"</span>,
       <span class="nt"> "interval":</span> <span class="s">"30s"</span> ,
       <span class="nt"> "timeout": </span><span class="s">"1m"</span> 
    },
    {
        <span class="nt">"name"</span> : <span class="s">"tcp_cassandra"</span>,
        <span class="nt">"tcp"</span> :  <span class="s">"http://localhost:9200"</span>,
       <span class="nt"> "interval":</span> <span class="s">"5m"</span> ,
       <span class="nt"> "timeout": </span><span class="s">"1m"</span> 
    }
  ]
                          
 }
                        </pre>
            </div>
            <div class="customform admonition ">
                <p class="pagerdutygif"><img class="testbtn" src="../../img/healthcheckseditor.png" alt="healthcheckseditor"></p>
            </div>

            <li>
                <p> <code>delete service(s)</code> </p>
                <p> To <span style="color:red">Delete</span> a service   <code>copy</code> and <code>Paste</code> inside. and click <code>save</code>
                    <img class="testbtn" src="../../img/disk.png" alt="save"></p>

            </li>
            <div class="codehilite">
                    <pre> {
      <span class="nt">"shellchecks":</span> [],
      <span class="nt">"httpchecks":</span> [],
      <span class="nt">"tcpchecks":</span> []
                              
 }
                            </pre>
                </div>
                <div class="customform admonition ">
                        <p class="pagerdutygif"><img class="testbtn" src="../../img/deleteservices.png" alt="delete"></p>
                    </div>
        </ul>



    </li>



</ol>