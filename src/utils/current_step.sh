#!/bin/bash

wp=$1

here="\033[0;31m\t <-- You are here!\n\033[0m"

echo -e "\n>>> submit this steps sequentially for a complete NEMAT run... ([ ] \033[0;31m <-- You are here!\n\033[0m marks the last completed step)\n"

if [ -d $wp ]; then
    if [ -d $wp/em_jobscripts ]; then
        count=$(cd $wp/em_jobscripts/ && find . -maxdepth 1 -type f -name "*.out" | wc -l)
        if [ $count -gt 0 ]; then
            if [ -d $wp/eq_jobscripts ]; then
                count=$(cd $wp/eq_jobscripts/ && find . -maxdepth 1 -type f -name "*.out" | wc -l)
                if [ $count -gt 0 ]; then
                    if [ -d $wp/md_jobscripts ]; then
                        count=$(cd $wp/md_jobscripts/ && find . -maxdepth 1 -type f -name "*.out" | wc -l)
                        if [ $count -gt 0 ]; then
                            if [ -d $wp/transitions_jobscripts ]; then
                                count=$(cd $wp/transitions_jobscripts/ && find . -maxdepth 1 -type f -name "*.out" | wc -l)
                                if [ $count -gt 0 ]; then
                                    echo -e "\t \033[0;32m1.\033[0m Prepare the system        : \033[1;33mnemat prep\033[0m\n"
                                    echo -e "\t \033[0;32m2.\033[0m Prepare minimization      : \033[1;33mnemat prep_min\033[0m"
                                    echo -e "\t \033[0;32m3.\033[0m Run minimization          : \033[1;33mnemat run_min\033[0m\n"
                                    echo -e "\t \033[0;32m4.\033[0m Prepare equilibration     : \033[1;33mnemat prep_eq\033[0m"
                                    echo -e "\t \033[0;32m5.\033[0m Run equilibration         : \033[1;33mnemat run_eq\033[0m\n"
                                    echo -e "\t \033[0;32m6.\033[0m Prepare production        : \033[1;33mnemat prep_md\033[0m"
                                    echo -e "\t \033[0;32m7.\033[0m Run production            : \033[1;33mnemat run_md\033[0m\n"
                                    echo -e "\t \033[0;32m8.\033[0m Prepare transitions       : \033[1;33mnemat prep_ti\033[0m"
                                    echo -e "       [ \033[0;32m9.\033[0m Run transitions           : \033[1;33mnemat run_ti\033[0m ] $here" 
                                    # echo -e "$here"
                                else
                                    echo -e "\t \033[0;32m1.\033[0m Prepare the system        : \033[1;33mnemat prep\033[0m\n"
                                    echo -e "\t \033[0;32m2.\033[0m Prepare minimization      : \033[1;33mnemat prep_min\033[0m"
                                    echo -e "\t \033[0;32m3.\033[0m Run minimization          : \033[1;33mnemat run_min\033 [0m\n"
                                    echo -e "\t \033[0;32m4.\033[0m Prepare equilibration     : \033[1;33mnemat prep_eq\033[0m"
                                    echo -e "\t \033[0;32m5.\033[0m Run equilibration         : \033[1;33mnemat run_eq\033[0m\n"
                                    echo -e "\t \033[0;32m6.\033[0m Prepare production        : \033[1;33mnemat prep_md\033[0m"
                                    echo -e "\t \033[0;32m7.\033[0m Run production            : \033[1;33mnemat run_md\033[0m\n"
                                    echo -e "       [ \033[0;32m8.\033[0m Prepare transitions       : \033[1;33mnemat prep_ti\033[0m ] $here\n"
                                    echo -e "\t 9. Run transitions           : \033[1;33mnemat run_ti\033[0m\n"
                                fi
                            else
                                echo -e "\t \033[0;32m1.\033[0m Prepare the system        : \033[1;33mnemat prep\033[0m\n"
                                echo -e "\t \033[0;32m2.\033[0m Prepare minimization      : \033[1;33mnemat prep_min\033[0m"
                                echo -e "\t \033[0;32m3.\033[0m Run minimization          : \033[1;33mnemat run_min\033[0m\n"
                                echo -e "\t \033[0;32m4.\033[0m Prepare equilibration     : \033[1;33mnemat prep_eq\033[0m"
                                echo -e "\t \033[0;32m5.\033[0m Run equilibration         : \033[1;33mnemat run_eq\033[0m\n"
                                echo -e "\t \033[0;32m6.\033[0m Prepare production        : \033[1;33mnemat prep_md\033[0m"
                                echo -e "       [ \033[0;32m7.\033[0m Run production            : \033[1;33mnemat run_md\033[0m ] $here\n"
                                echo -e "\t 8. Prepare transitions       : \033[1;33mnemat prep_ti\033[0m"
                                echo -e "\t 9. Run transitions           : \033[1;33mnemat run_ti\033[0m\n"
                            fi

                        else
                            echo -e "\t \033[0;32m1.\033[0m Prepare the system        : \033[1;33mnemat prep\033[0m\n"
                            echo -e "\t \033[0;32m2.\033[0m Prepare minimization      : \033[1;33mnemat prep_min\033[0m"
                            echo -e "\t \033[0;32m3.\033[0m Run minimization          : \033[1;33mnemat run_min\033[0m\n"
                            echo -e "\t \033[0;32m4.\033[0m Prepare equilibration     : \033[1;33mnemat prep_eq\033[0m"
                            echo -e "\t \033[0;32m5.\033[0m Run equilibration         : \033[1;33mnemat run_eq\033[0m\n"
                            echo -e "       [ \033[0;32m6.\033[0m Prepare production        : \033[1;33mnemat prep_md\033[0m ] $here"
                            echo -e "\t 7. Run production            : \033[1;33mnemat run_md\033[0m\n"
                            echo -e "\t 8. Prepare transitions       : \033[1;33mnemat prep_ti\033[0m"
                            echo -e "\t 9. Run transitions           : \033[1;33mnemat run_ti\033[0m\n"
                        fi

                    else
                        echo -e "\t \033[0;32m1.\033[0m Prepare the system        : \033[1;33mnemat prep\033[0m\n"
                        echo -e "\t \033[0;32m2.\033[0m Prepare minimization      : \033[1;33mnemat prep_min\033[0m"
                        echo -e "\t \033[0;32m3.\033[0m Run minimization          : \033[1;33mnemat run_min\033[0m\n"
                        echo -e "\t \033[0;32m4.\033[0m Prepare equilibration     : \033[1;33mnemat prep_eq\033[0m"
                        echo -e "       [ \033[0;32m5.\033[0m Run equilibration         : \033[1;33mnemat run_eq\033[0m ] $here\n"
                        echo -e "\t 6. Prepare production        : \033[1;33mnemat prep_md\033[0m"
                        echo -e "\t 7. Run production            : \033[1;33mnemat run_md\033[0m\n"
                        echo -e "\t 8. Prepare transitions       : \033[1;33mnemat prep_ti\033[0m"
                        echo -e "\t 9. Run transitions           : \033[1;33mnemat run_ti\033[0m\n"
                    fi

                else
                    echo -e "\t \033[0;32m1.\033[0m Prepare the system        : \033[1;33mnemat prep\033[0m\n"
                    echo -e "\t \033[0;32m2.\033[0m Prepare minimization      : \033[1;33mnemat prep_min\033[0m"
                    echo -e "\t \033[0;32m3.\033[0m Run minimization          : \033[1;33mnemat run_min\033[0m\n"
                    echo -e "       [ \033[0;32m4.\033[0m Prepare equilibration     : \033[1;33mnemat prep_eq\033[0m ] $here"
                    echo -e "\t 5. Run equilibration         : \033[1;33mnemat run_eq\033[0m\n"
                    echo -e "\t 6. Prepare production        : \033[1;33mnemat prep_md\033[0m"
                    echo -e "\t 7. Run production            : \033[1;33mnemat run_md\033[0m\n"
                    echo -e "\t 8. Prepare transitions       : \033[1;33mnemat prep_ti\033[0m"
                    echo -e "\t 9. Run transitions           : \033[1;33mnemat run_ti\033[0m\n"
                fi

            else
                echo -e "\t \033[0;32m1.\033[0m Prepare the system        : \033[1;33mnemat prep\033[0m\n"
                echo -e "\t \033[0;32m2.\033[0m Prepare minimization      : \033[1;33mnemat prep_min\033[0m"
                echo -e "       [ \033[0;32m3.\033[0m Run minimization          : \033[1;33mnemat run_min\033[0m ] $here\n"
                echo -e "\t 4. Prepare equilibration     : \033[1;33mnemat prep_eq\033[0m"                
                echo -e "\t 5. Run equilibration         : \033[1;33mnemat run_eq\033[0m\n"
                echo -e "\t 6. Prepare production        : \033[1;33mnemat prep_md\033[0m"
                echo -e "\t 7. Run production            : \033[1;33mnemat run_md\033[0m\n"
                echo -e "\t 8. Prepare transitions       : \033[1;33mnemat prep_ti\033[0m"
                echo -e "\t 9. Run transitions           : \033[1;33mnemat run_ti\033[0m\n"
            fi

        else
            echo -e "\t \033[0;32m1.\033[0m Prepare the system        : \033[1;33mnemat prep\033[0m\n"
            echo -e "       [ \033[0;32m2.\033[0m Prepare minimization      : \033[1;33mnemat prep_min\033[0m ] $here"
            echo -e "\t 3. Run minimization          : \033[1;33mnemat run_min\033[0m\n"
            echo -e "\t 4. Prepare equilibration     : \033[1;33mnemat prep_eq\033[0m"
            echo -e "\t 5. Run equilibration         : \033[1;33mnemat run_eq\033[0m\n"
            echo -e "\t 6. Prepare production        : \033[1;33mnemat prep_md\033[0m"
            echo -e "\t 7. Run production            : \033[1;33mnemat run_md\033[0m\n"
            echo -e "\t 8. Prepare transitions       : \033[1;33mnemat prep_ti\033[0m"
            echo -e "\t 9. Run transitions           : \033[1;33mnemat run_ti\033[0m\n"
        fi
    
    else
        echo -e "       [ \033[0;32m1.\033[0m Prepare the system        : \033[1;33mnemat prep\033[0m ] $here"
        echo -e "\t 2. Prepare minimization      : \033[1;33mnemat prep_min\033[0m"
        echo -e "\t 3. Run minimization          : \033[1;33mnemat run_min\033[0m\n"
        echo -e "\t 4. Prepare equilibration     : \033[1;33mnemat prep_eq\033[0m"
        echo -e "\t 5. Run equilibration         : \033[1;33mnemat run_eq\033[0m\n"
        echo -e "\t 6. Prepare production        : \033[1;33mnemat prep_md\033[0m"
        echo -e "\t 7. Run production            : \033[1;33mnemat run_md\033[0m\n"
        echo -e "\t 8. Prepare transitions       : \033[1;33mnemat prep_ti\033[0m"
        echo -e "\t 9. Run transitions           : \033[1;33mnemat run_ti\033[0m\n"
    fi

else
    echo -e "       [ \033[0;32m1.\033[0m Prepare the system        : \033[1;33mnemat prep\033[0m ] $here"
    echo -e "\t 2. Prepare minimization      : \033[1;33mnemat prep_min\033[0m"
    echo -e "\t 3. Run minimization          : \033[1;33mnemat run_min\033[0m\n"
    echo -e "\t 4. Prepare equilibration     : \033[1;33mnemat prep_eq\033[0m"
    echo -e "\t 5. Run equilibration         : \033[1;33mnemat run_eq\033[0m\n"
    echo -e "\t 6. Prepare production        : \033[1;33mnemat prep_md\033[0m"
    echo -e "\t 7. Run production            : \033[1;33mnemat run_md\033[0m\n"
    echo -e "\t 8. Prepare transitions       : \033[1;33mnemat prep_ti\033[0m"
    echo -e "\t 9. Run transitions           : \033[1;33mnemat run_ti\033[0m\n"
fi

echo -e "\t10. Analyze results           : \033[1;33mnemat analyze\033[0m\n"