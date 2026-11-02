// Contract QA fixtures. Never copied to student/ or served by the app.
// Template bodies only throw and cannot pass exercises. No solutions here.
#pragma once
#include <cstddef>
#include <iostream>
#include <string>
#include <stdexcept>
#include <typeinfo>
#include "support.hpp"
class Polynomial2 {
public:
 Polynomial2(double=0,double=0,double=0);
 double& operator[](std::size_t); const double& operator[](std::size_t)const;
 double operator()(double)const;
 Polynomial2 operator+(const Polynomial2&)const; Polynomial2 operator-(const Polynomial2&)const;
 Polynomial2 operator+()const; Polynomial2 operator-()const; Polynomial2 operator*(double)const;
 bool operator==(const Polynomial2&)const; bool operator!=(const Polynomial2&)const;
 friend Polynomial2 operator*(double,const Polynomial2&); friend std::ostream& operator<<(std::ostream&,const Polynomial2&);
};
class CMyString {
public:
 CMyString();explicit CMyString(const char*);CMyString(const CMyString&);CMyString& operator=(const CMyString&);~CMyString();
 std::size_t size()const;const char* c_str()const;char& operator[](std::size_t);const char& operator[](std::size_t)const;
 bool operator==(const CMyString&)const;bool operator!=(const CMyString&)const;
 CMyString operator+(const CMyString&)const;CMyString& operator+=(const CMyString&);CMyString operator!()const;CMyString operator^(int)const;
 CMyString operator()(int,...)const;void erase(std::size_t,std::size_t);void replace_range(std::size_t,std::size_t,const char*);
 explicit operator const char*()const;
 friend std::ostream& operator<<(std::ostream&,const CMyString&);friend std::istream& operator>>(std::istream&,CMyString&);
};
class BadText{public:explicit BadText(const char*);BadText(const BadText&);BadText& operator=(const BadText&);~BadText();char& operator[](std::size_t);const char* c_str()const;};
char* concat_copy(const char*,const char*);int compare_text(const char*,const char*);void copy_ints(int*,const int*,std::size_t);void shift_left(char*,std::size_t);
int checked_access(const int*,std::size_t,std::size_t);
template<class T>T maximum(T,T){throw std::logic_error("declaration fixture");}
const char* maximum(const char*,const char*);
template<class T>void swap_values(T&,T&);
template<class T>T minimum_of_three(T,T,T){throw std::logic_error("declaration fixture");}
template<class T>std::size_t index_of_min(const T*,std::size_t);
template<class T,class P>std::size_t find_first(const T*,std::size_t,P){throw std::logic_error("declaration fixture");}
template<class T,class P>std::size_t count_if(const T*,std::size_t,P){throw std::logic_error("declaration fixture");}
template<class T>void swap_at(T*,std::size_t,std::size_t,std::size_t);
template<class T>class Box{public:explicit Box(const T&);const T& get()const;void set(const T&);};
template<class T,int N=256>class FixedBuffer{public:T& operator[](std::size_t);const T& operator[](std::size_t)const;std::size_t capacity()const;};
template<class T>class AbstractStack{public:virtual ~AbstractStack()=default;virtual bool Push(const T&)=0;virtual bool Pop(T&)=0;virtual bool Get(T&)const=0;virtual std::size_t Count()const=0;virtual bool Empty()const=0;virtual bool Full()const=0;};
#define STACK_DECL bool Push(const T&)override;bool Pop(T&)override;bool Get(T&)const override;std::size_t Count()const override;bool Empty()const override;bool Full()const override
template<class T,int N=256>class TFixedStack:public AbstractStack<T>{public:STACK_DECL;};
template<class T>class DynamicStack:public AbstractStack<T>{public:STACK_DECL;};
template<class T>class SingleStack:public AbstractStack<T>{public:STACK_DECL;};
#undef STACK_DECL
template<class T>class TextStack;
template<>class TextStack<char*>{public:bool Push(const char*);bool Pop();const char* Get()const;std::size_t Count()const;bool Empty()const;};
template<class T>bool round_trip(AbstractStack<T>&,const T&,const T&,T&,T&);
struct Shape{virtual ~Shape()=default;virtual double area()const=0;};
struct Rectangle:Shape{Rectangle(double,double);double area()const override;};
struct Circle:Shape{explicit Circle(double);double area()const override;};
Rectangle* as_rectangle(Shape*);Rectangle& require_rectangle(Shape&);bool is_exact_circle(const Shape&);Shape* upcast(Rectangle*);
template<class T>class TSequence {
public:
 TSequence();explicit TSequence(std::size_t);TSequence(const TSequence&);TSequence& operator=(const TSequence&);~TSequence();
 TSequence(TSequence&&)noexcept;TSequence& operator=(TSequence&&)noexcept;
 std::size_t size()const;bool empty()const;T& operator[](std::size_t);const T& operator[](std::size_t)const;
 void push_back(const T&);void insert(std::size_t,const T&);void erase(std::size_t);
 bool operator==(const TSequence&)const;bool operator!=(const TSequence&)const;
};
template<class T>std::ostream& operator<<(std::ostream&,const TSequence<T>&);
template<class T>TSequence<T> reversed_copy(const TSequence<T>&);
