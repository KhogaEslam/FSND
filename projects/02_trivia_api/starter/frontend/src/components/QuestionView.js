import React, { Component } from 'react';

import constConfigObject from './constants';
import '../stylesheets/App.css';
import Question from './Question';
import Search from './Search';
import $ from 'jquery';

class QuestionView extends Component {
  constructor(){
    super();
    this.state = {
      questions: [],
      page: 1,
      totalQuestions: 0,
      categories: [],
      currentCategory: null,
    }
  }

  componentDidMount() {
    this.getQuestions();
  }

  getQuestions = () => {
    $.ajax({
      url: `${constConfigObject.BASE_URL}/questions?page=${this.state.page}`,
      type: "GET",
      success: (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
          categories: result.categories,
          currentCategory: result.current_category })
        return;
      },
      error: (error) => {
        alert('Unable to load questions. Please try your request again')
        return;
      }
    })
  }

  selectPage(num) {
    this.setState({page: num}, () => this.getQuestions());
  }

  createPagination(){
    let pageNumbers = [];
    let maxPage = Math.ceil(this.state.totalQuestions / 10)
    for (let i = 1; i <= maxPage; i++) {
      pageNumbers.push(
        <span
          key={i}
          className={`page-num ${i === this.state.page ? 'active' : ''}`}
          onClick={() => {this.selectPage(i)}}>{i}
        </span>)
    }
    return pageNumbers;
  }

  getByCategory= (id) => {
    $.ajax({
      url: `${constConfigObject.BASE_URL}/categories/${id}/questions`,
      type: "GET",
      success: (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
          currentCategory: result.current_category,
        });
        return;
      },
      error: (error) => {
        alert("Unable to load questions. Please try your request again");
        return;
      },
    });
  }

  submitSearch = (searchTerm) => {
    $.ajax({
      url: `${constConfigObject.BASE_URL}/questions/search`,
      type: "POST",
      dataType: "json",
      contentType: "application/json",
      data: JSON.stringify({ searchTerm: searchTerm }),
      xhrFields: {
        withCredentials: true,
      },
      crossDomain: true,
      success: (result) => {
        this.setState({
          questions: result.questions ? result.questions : [],
          totalQuestions: result.total_questions ? result.total_questions : 0,
          currentCategory: result.current_category,
        });
        return;
      },
      error: (error) => {
        alert("Unable to load questions. Please try your request again");
        return;
      },
    });
  }

  questionAction = (id) => (action) => {
    if(action === 'DELETE') {
      if(window.confirm('are you sure you want to delete the question?')) {
        $.ajax({
          url: `${constConfigObject.BASE_URL}/questions/${id}`,
          type: "DELETE",
          success: (result) => {
            this.getQuestions();
          },
          error: (error) => {
            alert("Unable to load questions. Please try your request again");
            return;
          },
        });
      }
    }
  }

  getCategory = (categoryID) => {
    return this.state.categories.filter(category => {
      return category.id === categoryID
    })[0].type
  }

  render() {
    return (
      <div className="question-view">
        <div className="categories-list">
          <h2 onClick={() => {this.getQuestions()}}>Categories</h2>
          <ul>
            {this.state.categories.map((category, idx) => (
              <li key={category.id} onClick={() => {this.getByCategory(category.id)}}>
                <img className="category" src={`${category.type}.svg`} alt={category.type} />
                {category.type}
              </li>
            ))}
          </ul>
          <Search submitSearch={this.submitSearch}/>
        </div>
        <div className="questions-list">
          <h2>Questions ({this.state.totalQuestions})</h2>
          {this.state.questions.map((q, ind) => (
            <Question
              key={q.id}
              question={q.question}
              answer={q.answer}
              category={this.getCategory(q.category)} 
              difficulty={q.difficulty}
              questionAction={this.questionAction(q.id)}
            />
          ))}
          <div className="pagination-menu">
            {this.createPagination()}
          </div>
        </div>

      </div>
    );
  }
}

export default QuestionView;
