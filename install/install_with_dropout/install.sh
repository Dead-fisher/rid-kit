#!/bin/bash

conda install libtensorflow_cc -c yfb222333

SoftwarePath=$HOME/software
RiDkit_Path=$(pwd)
mkdir $SoftwarePath

cd $SoftwarePath

wget -q https://github.com/Dead-fisher/rid-kit/releases/download/v1.0/gromacs-dp-rid-0.0.5-float-gpu-Linux-x86_64.sh > download.log
sh gromacs-dp-rid-0.0.5-float-gpu-Linux-x86_64.sh
RiDEnvPath=$HOME/gromacs-dp-rid

wget https://github.com/plumed/plumed2/releases/download/v2.5.7/plumed-2.5.7.tgz
tar -xvzf plumed-2.5.7.tgz
PLUMED_Src_Path=${SoftwarePath}/plumed-2.5.7
cp $RiDkit_Path/install/install_with_dropout/DeePFE.cpp plumed-2.5.7/src/bias
cd plumed-2.5.7
export tf_path="${RiDEnvPath}/lib/python3.6/site-packages/tensorflow"
PLUMED_Install_Path=${SoftwarePath}/plumed-2.5.7-test
./configure --prefix=${PLUMED_Install_Path} CXXFLAGS="-std=gnu++11 -I $tf_path/include/" LDFLAGS=" -L$tf_path/lib -ltensorflow_framework -ltensorflow_cc -Wl,-rpath,$tf_path/lib/" 
make
make install
export PATH="${PLUMED_Src_Path}/src/lib/:$PATH"
export LIBRARY_PATH="${PLUMED_Src_Path}/src/lib/:$LIBRARY_PATH"
export LD_LIBRARY_PATH="${PLUMED_Src_Path}/src/lib/:$LD_LIBRARY_PATH"
export PLUMED_KERNEL="${PLUMED_Src_Path}/src/lib/libplumedKernel.so"
export PLUMED_VIMPATH="${PLUMED_Src_Path}/vim"
export PYTHONPATH="${PLUMED_Src_Path}/python:$PYTHONPATH"

source /home/dongdong/wyz/software/gromacs-2019.2-mod-2022/bin/GMXRC.bash
