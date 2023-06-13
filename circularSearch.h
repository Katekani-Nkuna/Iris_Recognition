#ifndef CIRCULARSEARCH_H_INCLUDED
#define CIRCULARSEARCH_H_INCLUDED

#include <opencv2/opencv.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui_c.h>
#include <vector>
#include <cmath>


using namespace std;
using namespace cv;

double  lineInegral(Mat& img,double c0,double c1,double r,int n,char part)
{
    double theta = (2*M_PI)/n;
    double angle;
    double step;
    int x[n];
    int y[n];
    double length;
    int pixel;


    int rows = img.rows;
    int cols = img.cols;

    //Smallest angle subtended by centre to corner of polygon
    step = (2*M_PI-theta)/(n-1);
    for(int i = 0; i < n; i++)
    {
        //All the angles subtended by centre to all corners of polygon
        angle = (i+1)*step;
        //get the pixel locations
        x[i] = round(c0 - r*sin(angle));
        //Should any of the points lie outside the image matrix, then it cannot possibly be iris region
        if(x[i] >= rows || x[i] <= 0)
            return -1;

        y[i] = round(c1 + r*cos(angle));
        //Should any of the points lie outside the image matrix, then it cannot possibly be iris region
        if(y[i] >= cols || y[i] <= 0)
            return -1;
    }

    /*Now calculating the Normalized line integral*/
    if(part == 'p')
    {
        length = 0;

        for(int i = 0; i < n; i++)
        {
            pixel = img.at<uchar>(x[i],y[i]);
            length = length + pixel;
        }

        return length/n;
    }
    else
    {
        length = 0.0;


        for(int i = 0;i < n/8; i++)
        {
            pixel = img.at<uchar>(x[i],y[i]);
            length = length + pixel;
        }


        for(int i = (3*n)/8;i < (5*n)/8; i++)
        {
            pixel = img.at<uchar>(x[i],y[i]);
            length = length + pixel;
        }

        for(int i = (7*n)/8;i < n; i++)
        {
            pixel = img.at<uchar>(x[i],y[i]);
            length = length + pixel;
        }

        return (2.0*length)/n;
    }

}

/*Function to calculate the partial derivative of the line integral*/
vector<double> partialDerivative(Mat& img, double xc, double yc, int rmin, int rmax, double sigma, int n, char part)
{
    int samples = rmax - rmin;
    double R[samples];
    double integral;
    double previous_integral;
    vector<double> partial_derivatives;
    int maxIndex;
    double maxBlur;
    vector<double> results(2);
    int n_ = 0;

    /*Create array of Radius rmin - rmax*/
    for(int i = 0; i < samples; i++)
    {
        R[i] = rmin++;
    }

    /*Compute the partial derivatives of the line integrals between adjacent circles R[i]*/
    for(int i = 0; i < samples; i++)
    {
        /*Calculate the line integral of circle with radius R[i]*/
        n_ = (n*R[i])/30;
        integral = lineInegral(img,xc,yc,R[i],n_,part);

        if(integral < 0)
        {
            break;
        }

        if(i == 0)
        {
            partial_derivatives.push_back(0);
            previous_integral = integral;
        }
        else
        {
            /*Calculate the partial derivative between adjacent line integrals of circle R[i] and R[i-1]*/
            partial_derivatives.push_back(integral - previous_integral);
            previous_integral = integral;
        }
    }


    GaussianBlur(partial_derivatives,partial_derivatives,Size(5,1),sigma);

    /*get maximum blur and index of maximum blur*/

    maxIndex = 0;
    maxBlur = 0;
    for(int i = 0; i< partial_derivatives.size(); i++)
    {
        if(abs(partial_derivatives[i]) > maxBlur)
        {
            maxBlur = abs(partial_derivatives[i]);
            maxIndex = i;
        }
    }

    results[0] = maxBlur;
    results[1] = R[maxIndex];

    return results;

}

/*Function to search for the pupil or the iris region, assumming a centre x,y*/
vector<double> searchFor(Mat& img, int rmin, int rmax, int x, int y, int n, char part)
{
    int rows = img.rows;
    int cols = img.cols;
    double max_radius[rows][cols];
    double max_blur[rows][cols];
    vector<double> maximum;
    double sigma = 0.5;
    vector<double> centre(3,0);
    double max_b = 0;

    /*Search around a 10*10 neigbour*/
    for(int i = x-5; i< x+5; i++)
    {
        for(int j = y-5; j < y+5; j++)
        {
            maximum = partialDerivative(img,i,j,rmin,rmax,sigma,n,part);
            /*Get coordinate and rudius where maxblur occurs*/
            if(max_b < maximum[0])
            {
                max_b = maximum[0];
                centre[0] = i;
                centre[1] = j;
                centre[2] = maximum[1];
            }

        }
    }

    return centre;
}

/*This is the application of Daugman's Integro Differential Operator
  We are now using it to search for the iris
  then from that we find the pupil*/
vector<double> segment(Mat& img,Mat& bimg, int rmin, int rmax,int n, double scale, float thresh)
{
    Mat binary_image;
    int rows = img.rows;
    int cols = img.cols;
    float pixel;
    int ** index;
    vector<double> centre(3,0);
    vector<double> maximum;
    double max_b = 0;
    double max_rad = 0;
	int k = 0;


    vector<double> pupil_circle(3,0);
    vector<double> iris_circle(3,0);

    index = new int * [rows];
    for(int i = 0; i < rows; i ++)
    {
        index[i] = new int [cols];
    }
    /*Preprocessing*/

    /*Normalize the image such that, the pixel values are betwen [0,1]*/
    normalize(img, binary_image, 0.0, 1.0, cv::NORM_MINMAX,CV_32F);

    /*eleminating noisy pixels, thus localising the search center search to the pupil region (The centre of iris and pupil can only be at the pupil region)*/
    for(int i = 0; i < rows; i++)
    {
        for(int j = 0; j < cols; j++)
        {
            //pixel = binary_image.at<float>(i,j);
			pixel = bimg.at<uchar>(i,j);
            /*Eliminate all pixels that are greater than the threshold, they cannot possibly be part of the pupil*/
            if(pixel == 0)
            {
                /*Eliminate all pixels that are so close to the border, they cannot possibly be the centre of the pupil*/
                if((i > rmin) && (j > rmin) && (i < (rows-rmin)) && (j < (cols-rmin)))
                {	
                    /*Check if this is not noise, an outlying dark pixel far from the pupil region*/
                    if(binary_image.at<float>(i,j-1) < pixel || binary_image.at<float>(i-1,j-1) < pixel|| binary_image.at<float>(i,j-1)  < pixel||
                    binary_image.at<float>(i-1,j+1) < pixel || binary_image.at<float>(i,j+1) < pixel || binary_image.at<float>(i+1,j+1) < pixel || binary_image.at<float>(i+1,j) < pixel)
                    {
                        index[i][j] = -1;
                    }
                    else
                    {
                        index[i][j] = 1;		
						img.at<uchar>(i,j) = (uchar)0;
                    }
                }
                else
                {
                    index[i][j] = -1;
                }
            }
            else
            {
                index[i][j] = -1;
            }
        }
    }

	/*
	namedWindow( "Display window", WINDOW_AUTOSIZE );// Create a window for display.
    imshow( "Display window", bimg );
    waitKey(0);*/

    /*Now we can start applying daugman's algorithm*/
    cout<<"Searching for iris boundaries"<<endl;

    for(int i = 0; i < rows; i++)
    {
        for(int j = 0; j < cols; j++)
        {
            /*these are the noisy pixels, skip them*/
            if(index[i][j]  == -1)
            {
                continue;
            }
            //cout <<++k<<endl;
            //cout<<binary_image.at<float>(i,j)<<endl;

            maximum = partialDerivative(bimg,i,j,0.1*rmin,0.8*rmax,0.5,n,'p');
            /*the greatest blur is the radius*/
           if(max_b < maximum[0])
            {
                max_b = maximum[0];
                centre[0] = i;//y
                centre[1] = j;//x
                centre[2] = maximum[1];
            }
        }
    }

	
	cout<<centre[0]<<endl;
	cout<<centre[1]<<endl;
    pupil_circle = searchFor(bimg,0.1*rmin,0.8*rmax,centre[0],centre[1], n, 'p');

    //rmin = 0.3*iris_circle[2];
    //rmax = 0.7*iris_circle[2];

    int xi, yi, r, R;

    xi = pupil_circle[1], yi = pupil_circle[0], r = pupil_circle[2];

    /*Having found the pupil boundary, we now search for the iris boundary, limitting the search to the 10*10 neigbour of the detected pupil centre*/

    iris_circle = searchFor(img,rmin,rmax,pupil_circle[0],pupil_circle[1],n,'i');

    for(int i = 0 ;i < 3; i++)
    {
        iris_circle.push_back(pupil_circle[i]);
    }

    return iris_circle;
}

int getVideo()
{
    VideoCapture cap(1); // open the default camera
    if(!cap.isOpened())  // check if we succeeded
        return -1;

    Mat flipped;
    namedWindow("edges",1);
    for(;;)
    {
        Mat frame;
        Mat gray;
        Mat cropped;
        cap >> frame; // get a new frame from camera
        //GaussianBlur(frame, flipped, Size(7,7), 1.5, 1.5);
        cv::flip(frame,flipped,1);
        cv::cvtColor(flipped,gray,CV_BGR2GRAY);

        //circle(gray,Point(230,225),30,Scalar( 0, 255, 0 ), 2, 120);
        //circle(gray,Point(340,225),30,Scalar( 0, 255, 0 ), 2, 120);
        cv::Rect myROI(320, 225, 60, 60);
        rectangle(gray,myROI,Scalar( 0, 255, 0 ),2,120);
        cout<<gray.size()<<endl;

        imshow("flipped", gray);
        if(waitKey(30) >= 0)
        {
                gray(myROI).copyTo(cropped);
                imshow("flipped", cropped);
                if(waitKey(0) >= 0) break;
        }
    }
    // the camera will be deinitialized automatically in VideoCapture destructor
    return 0;
}

/*
=================================================================================================
============================ Functions for eyelid searching =====================================
=================================================================================================
*/

double  parabolic_Inegral(Mat& img,int n,double a, double b, double c,int x0, int lBound, int uBound, char part)
{
    int x[n];
    int y[n];
    double length;

    int pixel;
    int rows = img.rows;
    int cols = img.cols;

    for(int i = 0; i < n; i++)
    {
        //get the pixel locations
        x[i] = i+x0;

        //Parabola curve fitting eyelid
        if(part == 'u')
        {
            y[i] = a*pow((x[i]-b),2)+c;
        }
        else
        {
            y[i] = -1*a*pow((x[i]-b),2)+c;
        }

          //Should any of the points lie outside the image matrix, then it cannot possibly be iris region
        if(x[i] >= cols || x[i] < 0)
        {
            return -1;
        }

        //Should any of the points lie outside the image matrix, then it cannot possibly be iris region
        if(y[i] >= rows || y[i] < 0)
        {
            return -1;
        }
    }

    /*Now calculating the Normalized line integral*/
    length = 0;

    int n_ = 0;
    for(int i = 0; i < n; i++)
    {
        if(part == 'u' && x[i] >= lBound && x[i] <= uBound)
            continue;

        pixel = img.at<uchar>(y[i],x[i]);
        length = length + pixel;
        n_++;
    }

    return length/n_;
}

vector<double> eyelid(Mat& img, double xc, double yc, double r, double sigma, char part)
{
    double integral;
    double previous_integral;
    vector<double> partial_derivatives;
    vector<double> gauss_blur;
    int maxIndex;
    double maxBlur;
    vector<double> results(3);
    int n_ = 0;
    double delta_a, delta_b = 1, delta_c = 1;
    double a, b, c;
    int i = 0;
    int n;
    int x0;
    vector<vector<double> > parabola;
    int cBound;
    int cBound0;

    n = 4*r;
    x0 = xc-2*r;
    delta_a = (1/(2*r))/10;
    int x[n];
    int y[n];

    if(part == 'u')
    {
        cBound = yc + 1*r/3;
        cBound0 = yc - r;
    }
    else
    {
        cBound = yc + r;
        cBound0 = yc + 2*r/3;
    }

    /*Calculate all line integrals of parabolas*/
    for(a = delta_a; a < 1/(2*r); a += delta_a)
    {
        results[0] = a;
        for(b = xc - r/2; b < xc + r/2; b += delta_b)
        {
            results[1] = b;
            for(c = cBound0; c < cBound; c += delta_c)
            {
                //Calculate the line integral of the parabola (a,b,c)
                results[2] = c;
                integral = parabolic_Inegral(img,n,a,b,c,x0,xc-r,xc+r,part);
               // cout<<integral<<endl;

                if(integral < 0)
                {
                    continue;
                }


                if(i == 0)
                {
                    partial_derivatives.push_back(0);
                    previous_integral = integral;
                    i++;
                }
                else
                {
                    /*Calculate the partial derivative between adjacent line integrals of parabola (a,b,c) and parabola (a,b,c-1)*/
                    partial_derivatives.push_back(integral - previous_integral);
                    previous_integral = integral;
                }
                parabola.push_back(results);
            }
            i = 0;
        }
        i = 0;
    }

    cout<<"Now Searching for eyelids"<<endl;
    cout<<partial_derivatives.size()<<endl;
    GaussianBlur(partial_derivatives,gauss_blur,Size(5,1),sigma);

    /*get maximum blur and index of maximum blur*/

    maxIndex = 0;
    maxBlur = 0;
    for(int i = 0; i< gauss_blur.size(); i++)
    {
        if(abs(gauss_blur[i]) > maxBlur)
        {
            maxBlur = abs(gauss_blur[i]);
            maxIndex = i;
        }
    }

    results[0] = parabola[maxIndex][0];
    results[1] = parabola[maxIndex][1];
    results[2] = parabola[maxIndex][2];

    return results;
}

#endif // CIRCULARSEARCH_H_INCLUDED
