# Setup Slack


<ol>
    <li>
        <div>
            <h5> Create Slack incoming WebHooks.</h5>
            <ul>
                <li>Go to Slack <code>Application</code></li>
                <li>On the side menu click <img class="testbtn" src="../../img/addslackapp.png" alt="addslackapp"> </li>
                <li>In search box type <code>Incoming Webhooks</code></li>
                <li>From the App directory click <code>Install</code> on <code>Incoming WebHooks App.</code></li>
                <div class="customform admonition">
                    <p class="pagerdutygif"><img src="../../img/incomingwebhook.gif" alt="incomingwebhook"></p>
                </div>
                <li><code>Click</code> Add Configuration </li>
                <div class="customform admonition">
                    <p class="pagerdutygif"><img src="../../img/AddConfigSLACK.png" alt="AddConfigSLACK"></p>
                </div>
                <li>In <code>Post to Channel</code> Box select an option from the<code>choose a channel</code> dropdown
                    menu .</li>
                <li><code>Click</code> <code>Add Incoming WebHooks Integration</code></li>
                <div class="customform admonition">
                    <p class="pagerdutygif"><img src="../../img/ChannelBoxSLACK.png" alt="ChannelBoxSLACK"></p>
                </div>
                <li id="step1"><code>Copy</code> and make a note of the <code>WebHook URL</code> that appears in the
                    <code>Setup Instructions</code>.</li>
                <div class="customform admonition">
                    <p class="pagerdutygif"><img src="../../img/SetupInstrucSLACK.png" alt="SetupInstrucSLACK"></p>
                </div>
            </ul>
        </div>
    </li>


    <li>

        <div>
            <h5> Insert Slack WebHook URL.</h5>
            <p>On the Axonops application menu, select <code>Alert & Notifications -> Integration </code>.</p>
            <p>On the <code>Setup</code> menu, move the cursor over the slack icon and <code>click</code> on the
                <code>Add</code> symbol
            </p>
            <div class="customform admonition">
                <p class="pagerdutygif"><img src="../../img/slackhover.gif" alt="slackhover"></p>
            </div>
        </div>

    </li>
    <li>

        <div>
            <h5> Complete the fields in the pop-up form</h5>
            <ul>
                <li>
                    <p> Enter <code>Group name</code> &amp; <code>WebHook URL</code> from <code> <a href="#step1">step 1</a>.</code>
                        and <code>click</code> <img class="testbtn" src="../../img/testb.png" height="23" width="42"
                            alt="testb"></p>
                </li>
                <div class="customform admonition">
                    <p class="pagerdutygif"><img src="../../img/setupslack.png" alt="setupslack"></p>
                </div>
                <li>
                    <p>To add additional <code>WebHook URLs</code> click on <img class="testbtn" src="../../img/plusbtn.png"
                            alt="testb">, enter the additional WebHook URL and <code>click</code> <img class="testbtn"
                            src="../../img/testb.png" height="23" width="42" alt="testb"> </p>
                </li>
                <div class="customform admonition">
                    <p class="pagerdutygif"><img src="../../img/anotherwebhookurl.png" alt="anotherwebhookurl"></p>
                </div>
                <li>
                    <p>To remove any <code>WebHook URL</code> click on<img class="testbtn" src="../../img/minusbtn.png"
                            alt="testb">
                    </p>
                </li>

                <li>
                    <p> Click <img class="testbtn" src="../../img/submit.png" height="auto" width="80" alt="submit">
                        and close the pop-up form, on the Integrtions Menu the Slack Icon should now read <code>Installed</code>.
                        </lip>
                </li>
                <div class="customform admonition">
                    <p class="pagerdutygif"><img align="top" src="../../img/installedslack.png" alt="installedslack">
                    </p>
                </div>

                <li>
                    <p>To Edit any <code>WebHook URL</code> click on<img src="../../img/edit.png" alt="testb">
                    </p>
                </li>
                <div class="customform admonition">
                    <p class="pagerdutygif"><img src="../../img/editslack.png" alt="editslack"></p>
                </div>
                <li>
                    <p>and press <img class="testbtn" src="../../img/minusbtn.png" alt="minusbtn"> to remove specific
                        <code>WebHook URL</code> or <img class="testbtn" src="../../img/delbtn.png" alt="delbtn"> to
                        remove <code>group of keys</code> and click <img class="testbtn" src="../../img/submit.png"
                            height="auto" width="80" alt="submit">
                    </p>
                </li>
                <li>
                    <p>To <span style="color:red">Remove</span> Slack <code>groups</code> move the cusror over the
                        pagerduty icon <code>click</code> on the <code>Delete</code> symbol and <code>Confirm</code></p>
                </li>
                <div class="customform admonition">
                    <p class="pagerdutygif"><img src="../../img/removeslack.gif" alt="removeslack"></p>
                </div>
            </ul>

        </div>

    </li>
    </ul>