//Framework

import React from 'react';

export default class Framework extends React.Component {
	constructor() {
		super();
	}

	static propTypes(){
		return {
		}
	}
	
	render(){
		var elements = [];
		if(!!this.props.headerComponent){
			elements.push(<this.props.headerComponent key="face" />);
		}
		elements.push(<p key="content">This is content</p>);
		if(!!this.props.footerComponent){
			elements.push(<this.props.footerComponent key="footer" />);
		}
		return (
			<div>
				{elements}
			</div>
		);
	}
}
