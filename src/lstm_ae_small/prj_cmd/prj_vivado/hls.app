<AutoPilot:project xmlns:AutoPilot="com.autoesl.autopilot.project" top="lstm" name="prj_vivado">
    <includePaths/>
    <libraryFlag/>
    <files>
        <file name="../../nnet_utils/" sc="0" tb="false" cflags="-std=c++0x" csimflags="" blackbox="false"/>
        <file name="/home/dimdano/Desktop/PRIVATEER/RNN_HLS_custom/lstm_ae_small/common/includes/xcl2" sc="0" tb="false" cflags="-std=c++0x" csimflags="" blackbox="false"/>
        <file name="../../../tb_lstm.cpp" sc="0" tb="1" cflags=" -std=c++0x -Wno-unknown-pragmas" csimflags=" -Wno-unknown-pragmas" blackbox="false"/>
        <file name="/home/dimdano/Desktop/PRIVATEER/RNN_HLS_custom/lstm_ae_small/common/includes/xcl2/xcl2.cpp" sc="0" tb="false" cflags="-std=c++0x" csimflags="" blackbox="false"/>
        <file name="../lstm_fpga.cpp" sc="0" tb="false" cflags="-std=c++0x" csimflags="" blackbox="false"/>
    </files>
    <solutions>
        <solution name="cmd_z7045_ae_r1" status=""/>
    </solutions>
    <Simulation argv="">
        <SimFlow name="csim" setup="false" optimizeCompile="false" clean="false" ldflags="" mflags=""/>
    </Simulation>
</AutoPilot:project>

