export interface PythonTask {
 id:string;number:number;week:number;day:number;week_title:string;title:string;difficulty:number;minutes:number;skills:string[];signature:string;description:string;rules:string;example:string;edges:string;bonus:string;sources_labels:string[];source_urls:string[];dependencies:string[];optional_topic:boolean;test_mode:string;starter_files:Record<string,string>;
}
export interface PythonState {status:'not_started'|'in_progress'|'completed'|'revisit';notes:string;difficulty:string;weakTopics:string[];bookmark:boolean;skipped:boolean;topicReady:boolean;external:boolean;localChecked:boolean}
export const emptyState:PythonState={status:'not_started',notes:'',difficulty:'',weakTopics:[],bookmark:false,skipped:false,topicReady:false,external:false,localChecked:false};
export const statusLabels={not_started:'Ещё не начато',in_progress:'В работе',completed:'Отмечено мной',revisit:'Нужно повторить'};
export interface PythonAttempt extends PythonState {id:number;created:string;qualified:boolean}
export interface PythonDetail {task:PythonTask;files:Record<string,string>;revision:string;state:PythonState;history:PythonAttempt[];solutionUnlocked:boolean}
export interface PythonProgress {states:Record<string,PythonState>;lastPath:string;manual:boolean}
export interface PythonCourse {course:string;weeks:{week:number;title:string;reference:string}[];tasks:PythonTask[]}
export interface PythonSolution {id:string;solution_files:Record<string,string>;explanation:string;manual_review?:string|boolean}
