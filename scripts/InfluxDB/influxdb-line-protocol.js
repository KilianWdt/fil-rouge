flowFile = session.get();
if (flowFile != null) {
    var StreamCallback = Java.type("org.apache.nifi.processor.io.StreamCallback");
    var IOUtils = Java.type("org.apache.commons.io.IOUtils");
    var StandardCharsets = Java.type("java.nio.charset.StandardCharsets");
    var error = false;
    var measure = "client1"
    var line = "";
    var sep = "\n"
    // Get attributes
    flowFile = session.write(flowFile, new StreamCallback(function (inputStream, outputStream) {
        var content = IOUtils.toString(inputStream, StandardCharsets.UTF_8); // message or content
        var message_content = {};
        var sensor = "";
        var date = "";
        var value = "";
        try {
        message_content = JSON.parse(content);
        for (key in message_content){
            if (key == 'SENSOR') {
                sensor = message_content[key]
            } else if (key == 'DATE') {
            date = message_content[key] * 1000 * 1000 * 1000
            } else if (key == 'VALUE') {
            value = message_content[key]
            }
        }
        line = measure + " " + sensor + "=" + value + " " + date + sep
        // Write output content
        outputStream.write(line.getBytes(StandardCharsets.UTF_8));

        } catch (e) {
        error = true;
        log.error('Something went wrong', e)
        outputStream.write(content.getBytes(StandardCharsets.UTF_8));
        }
    }));
    if (error) {
        session.transfer(flowFile, REL_FAILURE)
    } else {
        session.transfer(flowFile, REL_SUCCESS)
    }
}
