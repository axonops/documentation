# Setup alert rules

<ol>

    <li>

        <div>
            <h5> Insert Alert Rules credentials</h5>
            <p>On the Axonops application menu, click <code>Dashboards </code> and <code>select</code> required <strong>Dashboard</strong>.
                <code>eg. System</code></p>
            <p><code>Hover over </code> the desired Chart <title></title> <code>click</code> on the <img src="../../img/edit.png"
                    alt="testb">
                button.</p>
            <div class="customform admonition">
                <p class="pagerdutygif"><img src="../../img/createrule.gif" alt="createrule"></p>
            </div>
        </div>

    </li>
    <li>

        <div>
            <h5> Complete the fields in form</h5>
            <ul>
                <li>
                    <p> Below the chart <code>click</code> on the <code>alert</code> tab.</p>
                </li>
                <div class="customform admonition ">
                    <p class="pagerdutygif"><img class="testbtn" src="../../img/alertform.png" alt="alertform"></p>
                </div>
                <li>
                    <p> A form will appear</p>
                </li>
                <div class="customform admonition">
                    <p class="pagerdutygif"><img src="../../img/alertformfields.png" alt="alertformfields"></p>
                </div>


                <li>
                    <p> Complete Alert settings in <code>Comparator</code> <code>Warning value</code>or <code>Critical value</code>
                        or <strong>Both</strong>
                        and the <code>Duration</code> ==> (how often to check) <code>In</code></p>
                </li>
                <div class="customform admonition">
                    <p class="pagerdutygif"><img align="top" src="../../img/allertfields.png" alt="allertfields">
                    </p>
                </div>

                <li>
                    <p> <code>Annotations</code> </p>
                    <p>In the <code>Summary</code> box you can include <strong>free</strong> text &amp; type one <code>or</code>
                        many of the following <code>$labels</code></p>

                    <div class="codehilite">
                        <pre>
                        <span></span><span class="nt">$labels</span><span class="p">:</span>
                            <span class="nt">- cluster</span><span class="p">
                            <span class="nt">- dc</span><span class="p">
                            <span class="nt">- hostname</span><span class="p">
                            <span class="nt">- org</span><span class="p">
                            <span class="nt">- rack</span><span class="p">
                            <span class="nt">- type</span><span class="p">
                            <span class="nt">- keyspace</span><span class="p">
                        <span></span><span class="nt">$value</span><span class="p">:</span>
                          </pre>
                    </div>

                    <p>In the <code>Description </code> box you can include <strong>free</strong> along with one <code>or</code>
                        many of the above <code>$labels</code> </p>

                    <div class="admonition info">
                        <p class="admonition-title">Example </p>
                        <p><code>CPU usage per DC Alerts usage on {{ $labels.hostname }}  and cluster {{$labels.cluster}}  
                                    </code></p>
                    </div>

                    <div class="customform admonition">
                        <p class="pagerdutygif"><img src="../../img/annotations.png" alt="annotations"></p>
                    </div>

                </li>


                <li>
                    <p>Using the slider bar <img class="testbtn" src="../../img/sliderbar.png" alt="sliderbar"> you can
                        select any <a href="/integrations/overview">Integrations</a> </p>
                    <p>Then <code>click</code> on the <code>Info</code>, <code>Warning</code>, <code>Error</code>
                        icons, to select the group(s) of <a href="/integrations/overview">Integrations</a> for the
                        alert.</p>
                    <div class="customform admonition">
                        <p class="pagerdutygif"><img src="../../img/alertintegrations.png" alt="alertintegrations"></p>
                        <p class="pagerdutygif"><img src="../../img/alertintegrationswith.png" alt="alertintegrationswith"></p>
                    </div>
                    <div class="admonition info">
                        <p class="admonition-title">Not selecting integrations </p>
                        <p class="pagerdutygif">
                            If you do not select any specific <a href="/integrations/overview">Integrations</a> the
                            Alert will <strong>automatically</strong>
                            follow the <code>Global Dashboard Routing</code> <strong>or</strong> if this
                            has not been <a href="/how-to/setup-dashboards-global-integrations">setup</a> the <a href="/how-to/default-routing">Default
                                Routing </a>Integrations.
                        </p>
                    </div>
                </li>


            </ul>

        </div>

    </li>
    <li>
        <div>
            <h5> Edit - Delete and Aler rule</h5>
            <ul>
                <li>
                    <p>Edit <code>Alert Rule</code></p>
                    <p>On the Axonops application menu, click <code>Alerts &amp; Notifications </code> and <code>click</code>
                        Active.</p>

                    </p>
                    <p>
                        <code>Select</code> the <code>Alert Rules</code> tab and click <img class="testbtn" src="../../img/edit.png"
                            alt="delbtn">
                    </p>
                    <p>
                        <div class="customform admonition">
                            <p class="pagerdutygif"><img src="../../img/editalertrule.png" alt="editalertrule"></p>
                        </div>
                    </p>
                </li>
                <p>To <span style="color:red">Delete</span> An <code>Alert</code> <strong>Either...</strong> </p>
                <li>
                    <p>On the Axonops application menu, click <code>Dashboards </code> and <code>select</code> required
                        <strong>Dashboard</strong>.
                        <code>eg. System</code></p>
                    <p><code>Hover over </code> the desired Chart <title></title> <code>click</code> on the <img src="../../img/edit.png"
                            alt="testb">
                        button.</p>
                    <p> Below the chart <code>click</code> on the <code>alert</code> tab and <code>click</code> on the
                        <img class="testbtn" src="../../img/delbtn.png" alt="delbtn"> of the alert rule you want to
                        remove.
                    </p>
                </li>
                <p><strong>Or...</strong> </p>
                <li>
                    <p>On the Axonops application menu, click <code>Alerts &amp; Notifications </code> and <code>click</code>
                        Active.</p>

                    </p>
                    <p>
                        <code>Select</code> the <code>Alert Rules</code> tab and click <img class="testbtn" src="../../img/delbtn.png"
                            alt="delbtn">
                    </p>
                    <p>
                        <div class="customform admonition">
                            <p class="pagerdutygif"><img src="../../img/activealertrules.png" alt="activealertrules"></p>
                        </div>
                    </p>
                </li>
            </ul>
        </div>
    </li>
</ol>