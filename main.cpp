#include "circularSearch.h"
#include <iostream>
#include <python2.7/Python.h>
#include <string>
#include <stdlib.h>
#include <pthread.h> 
#include "DVPCamera.h"
using namespace std;

/*
Sarinal3
kelvinl3
maranl3
lowyfl3
weecml3
christinl3
chongpkl3
*
/*main functin to run segmentation code*/
int main(int argc, char ** argv)
{
 	Mat image;
	Mat binary_image;
    Mat lookUpTable(1, 256, CV_32F);
	vector<double> circles;
	vector<double> upper_lid;
	vector<double> lower_lid;

	int x0, xc, b, c, n;
	int xi, yi, xp, yp;
	int b_,c_,lw;
	int * x = 0;
	int * y = 0;

	int * y_ = 0;
	double a, a_, ri, rp, Ri, Rp;
	FILE * file;
	FILE * images;
	string str;
	char cstr[3];
	char filename[30];
	char bfilename[30];
	char mode[20];
	int input;
	Py_Initialize();
	char src[30];

	//getVideo();

	images = fopen("file.txt" , "r");
	if (file == NULL)
	{
		perror ("Error opening file");
	}
   	else
   	{
		/*Fill holes on the object First*/
		
		cout<<"Select Mode of Operation: [1. Enrollment or 2.Verification]"<<endl;
		cin>>input;

		if(input == 1)
		{
			//mode = "enroll";
			strcpy(mode,"enroll");
		}
		else
		{
			//mode = "verify";
			strcpy(mode,"verify");
		}
		
    	while (!feof (images))
     	{
       		if( fgets(src , 30,images) == NULL) 
				break;
       		
			fputs (src , stdin);
			strtok(src, "\n");

	//char filename[30] = "Database/";
	//char bfilename[30] = "Binary/";
			memset(filename, '\0', sizeof(filename));
			memset(bfilename, '\0', sizeof(bfilename));
			strcpy(filename,"Database/");
			strcpy(bfilename,"Binary/");
			

			strcat(filename,src);
			strcat(bfilename,src);

			cout<<filename<<endl;
			cout<<bfilename<<endl;
	
			argc = 1;
			argv[0] = filename; 
			PySys_SetArgv(argc, argv);
			file = fopen("fillholes.py","r");
			PyRun_SimpleFile(file, "fillholes.py");
			fclose(file);

			image = imread(filename , IMREAD_GRAYSCALE);
			binary_image = imread(bfilename , IMREAD_GRAYSCALE);
			
			//namedWindow( "Display window", WINDOW_AUTOSIZE );// Create a window for display.
    		//imshow( "Display window", binary_image);
   			//waitKey(0);

			

		  	if(! image.data )
			{
			  cout <<  "Could not open or find the image" << endl ;
			  return -1;
			}

			cout<<filename<<endl;

			lw = 2;//The plot lineWidth

			circles = segment(image,binary_image,50,65,100,1,0.1);

			xc = circles[1] , ri = circles[2], rp = circles[5];
			x0 = xc-2*ri;

			xi = circles[1], yi = circles[0], xp = circles[4], yp = circles[3];

			upper_lid = eyelid(image, circles[1], circles[0], circles[2], 0.5,'u');
			lower_lid = eyelid(image, circles[1], circles[0], circles[2], 0.5,'l');

			printf("Iris_Circle\t= [%d, %d ,%d]\n\n",(int)circles[0],(int)circles[1],(int)circles[2]);
			printf("Pupil_Circle\t= [%d, %d ,%d]\n\n",(int)circles[3],(int)circles[4],(int)circles[5]);
			printf("Upper Lid\t= [%.6f, %d ,%d]\n\n",upper_lid[0],(int)upper_lid[1],(int)upper_lid[2]);
			printf("lower Lid\t= [%.6f, %d ,%d]\n\n",lower_lid[0],(int)lower_lid[1],(int)lower_lid[2]);

			//Plot Iris circle
			circle(image,Point(circles[1],circles[0]),circles[2],Scalar( 255, 0, 0 ), lw, 120);

			//Plot Pupil circle
			circle(image,Point(circles[4],circles[3]),circles[5],Scalar( 255, 0, 0 ), lw, 120);


			//Get the parabola parameters of upper eyelid
			a = upper_lid[0], b = upper_lid[1], c = upper_lid[2];

			//Get the parabola parameters of the lower eyelid
			a_ = lower_lid[0], b_ = lower_lid[1], c_ = lower_lid[2];

			//Number of samples to plot
			n = 4.2*ri;

			x = new int[n];
			y = new int[n];
			y_ = new int[n];

			for(int i = 0; i < n; i++)
			{
				x[i] =i+x0;
				/*Get coordinates of Upper Eyelid*/
				y[i] = a*pow((x[i]-b),2)+c;

				/*Get coordinates of Upper Eyelid*/
				y_[i] = -1*a_*pow((x[i]-b_),2)+c_;
			}

			for(int i = 0; i < n-1; i++)
			{
				/*Plot Upper Eyelid*/
				line(image, Point(x[i],y[i]), Point(x[i+1],y[i+1]), Scalar(255,0,0), lw, 120);

				/*Plot Upper Eyelid*/
				line(image, Point(x[i],y_[i]), Point(x[i+1],y_[i+1]), Scalar(255,0,0), lw, 120);
			}

			/*Unwrapping the iris Region*/

			for(int i = 0; i < image.rows; i++)
			{
				for(int j = 0; j < image.cols; j++)
				{
				    /*IF we are within bounds*/
				    if(j > x0 && j < x0 + n)
				    {
				        /*If We are within bounds*/
				        Ri = pow(i-yi,2) + pow(j-xi,2);
				        Rp = pow(i-yp,2) + pow(j-xp,2);

				        if(Ri <= pow(ri,2) && Rp >= pow(rp,2))
				        {
				            if(i  > a*pow((j-b),2)+c)
				            {
				               if(i <-1*a_*pow((j-b_),2)+c_)
				                {
				                    continue;
				                }
				            }
				        }
				    }

				    image.at<uchar>(i,j) = (uchar)0;
				}
			}

			/*namedWindow( "Display window", WINDOW_AUTOSIZE );// Create a window for display.
			imshow( "Display window", image);
			waitKey(0);
			*/

			/*Pass The Passed Parameters to python code*/
			

			argc = 14;

			for(int i = 0, j = 0, k = 0; i < 12; i++)
			{
				if(i < 6)
				{
					//str = to_string(circles[i]);
					//cstr = const_cast<char*>(str.c_str());
					sprintf (cstr, "%d", int(circles[i]));
				}
				else if(j < 3)
				{
					//str = to_string(upper_lid[j++]);
					//cstr = const_cast<char*>(str.c_str());
					sprintf (cstr, "%f", upper_lid[j++]);
				}
				else if(k <3)
				{
					//str = to_string(lower_lid[k++]);
					//cstr = const_cast<char*>(str.c_str());
					sprintf (cstr, "%f", lower_lid[k++]);
				}
		
				argv[i] = new char[3];
				strcpy(argv[i],cstr);

			}
			argv[12] = filename;
			argv[13] = mode;

			PySys_SetArgv(argc, argv);
			file = fopen("create_template.py","r");
			PyRun_SimpleFile(file, "create_template.py");
	
			fclose(file);

			for(int i = 0; i < 12; i++)
			{
				delete argv[i];
				argv[i] = 0;
			}
		}
		fclose (images);
	}
	Py_Finalize();

    //getVideo();

  	return 0;
}





